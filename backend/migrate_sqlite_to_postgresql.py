#!/usr/bin/env python3
"""
Complete migration script to transfer data from SQLite to PostgreSQL
Run this AFTER creating PostgreSQL tables but BEFORE switching your .env

Usage:
    python migrate_sqlite_to_postgresql.py
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table
import psycopg2

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    print("🔄 DojoTracker Data Migration: SQLite → PostgreSQL")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Database URLs
    sqlite_url = 'sqlite:///dojotracker.db'
    postgres_url = f"postgresql://postgres:mypassword123@localhost:5433/dojotracker"
    
    print(f"📤 Source (SQLite): {sqlite_url}")
    print(f"📥 Target (PostgreSQL): {postgres_url.split('@')[0]}@****")
    
    try:
        # Create engines
        print("\n🔍 Testing database connections...")
        sqlite_engine = create_engine(sqlite_url)
        postgres_engine = create_engine(postgres_url)
        
        # Test SQLite connection and get tables
        with sqlite_engine.connect() as conn:
            result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
            sqlite_tables = [row[0] for row in result.fetchall()]
            print(f"✅ SQLite connection successful. Found {len(sqlite_tables)} tables")
            print(f"   Tables: {', '.join(sqlite_tables)}")
        
        # Test PostgreSQL connection and get tables
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            postgres_tables = [row[0] for row in result.fetchall()]
            print(f"✅ PostgreSQL connection successful. Found {len(postgres_tables)} tables")
            print(f"   Tables: {', '.join(postgres_tables)}")
        
        if not sqlite_tables:
            print("ℹ️ No tables found in SQLite database. Nothing to migrate.")
            return True
        
        if not postgres_tables:
            print("❌ No tables found in PostgreSQL database.")
            print("💡 Run the following commands first:")
            print("   1. Uncomment DATABASE_URL in .env")
            print("   2. Run: python app.py (to create tables)")
            print("   3. Comment out DATABASE_URL again")
            print("   4. Run this migration script")
            return False
        
        # Tables to migrate in order (respecting foreign key constraints)
        migration_order = [
            'users',                    # Must be first (other tables reference it)
            'user_preferences',         # References users
            'training_sessions',        # References users  
            'technique_progress',       # References users
            'technique_categories',     # Independent
            'technique_library',        # May reference categories
            'user_technique_bookmarks', # References users and techniques
            'exercise_categories',      # Independent
            'muscle_groups',           # Independent
            'equipment',               # Independent
            'exercises',               # References categories
            'workout_exercises',       # References training_sessions and exercises
            'favorite_exercises',      # References users
            'workout_plans',           # References users
            'workout_plan_exercises'   # References workout_plans
        ]
        
        migrated_tables = []
        total_rows_migrated = 0
        
        print(f"\n📋 Starting data migration...")
        print(f"📊 Migration order: {' → '.join(migration_order)}")
        
        for table_name in migration_order:
            if table_name in sqlite_tables and table_name in postgres_tables:
                try:
                    print(f"\n📋 Migrating table: {table_name}")
                    
                    # Get data from SQLite
                    with sqlite_engine.connect() as sqlite_conn:
                        result = sqlite_conn.execute(text(f'SELECT * FROM {table_name}'))
                        rows = result.fetchall()
                        columns = result.keys()
                    
                    if not rows:
                        print(f"   ⏭️ Table {table_name} is empty, skipping")
                        continue
                    
                    print(f"   📊 Found {len(rows)} rows to migrate")
                    
                    # Clear PostgreSQL table first (in case of re-runs)
                    with postgres_engine.connect() as postgres_conn:
                        postgres_conn.execute(text(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE'))
                        postgres_conn.commit()
                        print(f"   🧹 Cleared existing data in PostgreSQL {table_name}")
                    
                    # Convert rows to dictionaries and handle data types
                    data_dicts = []
                    for row in rows:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            value = row[i]
                            
                            # Handle JSON columns that might be stored as strings
                            json_columns = ['instructions', 'primary_muscles', 'secondary_muscles', 
                                          'equipment_needed', 'exercise_muscles', 'exercise_equipment']
                            if col in json_columns and isinstance(value, str):
                                try:
                                    # Validate JSON
                                    json.loads(value)
                                except:
                                    # If not valid JSON, wrap in array
                                    if value:
                                        value = json.dumps([value])
                                    else:
                                        value = json.dumps([])
                            
                            row_dict[col] = value
                        data_dicts.append(row_dict)
                    
                    # Insert data into PostgreSQL in batches
                    batch_size = 100
                    with postgres_engine.connect() as postgres_conn:
                        # Create insert statement
                        columns_str = ', '.join(columns)
                        placeholders = ', '.join([f':{col}' for col in columns])
                        insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
                        
                        # Execute batch insert
                        for i in range(0, len(data_dicts), batch_size):
                            batch = data_dicts[i:i + batch_size]
                            postgres_conn.execute(text(insert_sql), batch)
                            postgres_conn.commit()
                            print(f"   ✅ Inserted batch {i//batch_size + 1} ({len(batch)} rows)")
                    
                    print(f"   ✅ Successfully migrated {len(rows)} rows")
                    migrated_tables.append(table_name)
                    total_rows_migrated += len(rows)
                    
                except Exception as e:
                    print(f"   ❌ Error migrating {table_name}: {str(e)}")
                    print(f"   🔍 This might be due to missing foreign key references")
                    continue
            else:
                missing_from = []
                if table_name not in sqlite_tables:
                    missing_from.append("SQLite")
                if table_name not in postgres_tables:
                    missing_from.append("PostgreSQL")
                print(f"   ⚠️ Skipping {table_name} (missing from: {', '.join(missing_from)})")
        
        # Reset PostgreSQL sequences for auto-increment columns
        print(f"\n🔧 Resetting PostgreSQL sequences...")
        with postgres_engine.connect() as postgres_conn:
            for table in migrated_tables:
                try:
                    # Check if table has an 'id' column with a sequence
                    result = postgres_conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' 
                        AND column_name = 'id' 
                        AND column_default LIKE 'nextval%'
                    """))
                    
                    if result.fetchone():
                        # Get the maximum ID from the table
                        result = postgres_conn.execute(text(f'SELECT MAX(id) FROM {table}'))
                        max_id = result.scalar()
                        
                        if max_id is not None:
                            # Reset the sequence
                            postgres_conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id})"))
                            postgres_conn.commit()
                            print(f"   ✅ Reset sequence for {table} to {max_id}")
                        else:
                            print(f"   ℹ️ No data in {table}, sequence unchanged")
                    else:
                        print(f"   ℹ️ {table} has no auto-increment id column")
                        
                except Exception as e:
                    print(f"   ⚠️ Could not reset sequence for {table}: {e}")
        
        # Final verification
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successfully migrated {len(migrated_tables)} tables")
        print(f"   📈 Total rows migrated: {total_rows_migrated}")
        print(f"   📋 Migrated tables: {', '.join(migrated_tables)}")
        
        if migrated_tables:
            print(f"\n🎉 Migration completed successfully!")
            print(f"\n📝 Next steps:")
            print(f"   1. Uncomment DATABASE_URL in your .env file:")
            print(f"      DATABASE_URL=postgresql://postgres:mypassword123@localhost:5433/dojotracker")
            print(f"   2. Restart your Flask app: python app.py")
            print(f"   3. Test that your favorites and workouts appear")
            print(f"   4. If everything works, you can delete dojotracker.db")
            
            return True
        else:
            print(f"\n❌ No tables were migrated successfully")
            return False
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_postgresql_connection():
    """Test PostgreSQL connection with detailed error reporting"""
    try:
        postgres_url = f"postgresql://postgres:mypassword123@localhost:5433/dojotracker"
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connection successful!")
        print(f"   Version: {version}")
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL connection failed:")
        print(f"   Error: {e}")
        print(f"💡 Check:")
        print(f"   - PostgreSQL is running")
        print(f"   - Port 5433 is correct")
        print(f"   - Password 'mypassword123' is correct")
        print(f"   - Database 'dojotracker' exists")
        return False

if __name__ == '__main__':
    print("🔍 Testing PostgreSQL connection first...")
    if not test_postgresql_connection():
        print("\n❌ Fix PostgreSQL connection before running migration")
        sys.exit(1)
    
    print("\n" + "="*60)
    success = migrate_data()
    
    if success:
        print(f"\n✅ Migration completed successfully!")
        print(f"🎯 Your SQLite data is now in PostgreSQL!")
    else:
        print(f"\n❌ Migration failed!")
        print(f"💡 Check the errors above and try again")
        sys.exit(1)