#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this AFTER setting up PostgreSQL configuration but BEFORE deleting SQLite data

Usage:
    python migrate_to_postgresql.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import json

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Load environment variables
    load_dotenv()
    
    # Database URLs
    sqlite_url = 'sqlite:///dojotracker.db'
    postgres_url = os.getenv('DATABASE_URL')
    
    if not postgres_url or not postgres_url.startswith('postgresql://'):
        print("❌ No PostgreSQL DATABASE_URL found in environment")
        print("💡 Make sure your .env file has a PostgreSQL DATABASE_URL")
        return False
    
    print("🔄 Starting data migration from SQLite to PostgreSQL")
    print(f"📤 Source: {sqlite_url}")
    print(f"📥 Target: {postgres_url.split('@')[0]}@****")
    
    try:
        # Create engines
        sqlite_engine = create_engine(sqlite_url)
        postgres_engine = create_engine(postgres_url)
        
        # Test connections
        print("\n🔍 Testing database connections...")
        
        with sqlite_engine.connect() as conn:
            result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
            sqlite_tables = [row[0] for row in result.fetchall()]
            print(f"✅ SQLite connection successful. Found {len(sqlite_tables)} tables")
        
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            postgres_tables = [row[0] for row in result.fetchall()]
            print(f"✅ PostgreSQL connection successful. Found {len(postgres_tables)} tables")
        
        if not sqlite_tables:
            print("ℹ️ No tables found in SQLite database. Nothing to migrate.")
            return True
        
        if not postgres_tables:
            print("❌ No tables found in PostgreSQL database.")
            print("💡 Run 'python app.py' first to create the PostgreSQL tables")
            return False
        
        # Tables to migrate (in order due to foreign key constraints)
        migration_order = [
            'users',
            'training_sessions', 
            'technique_progress',
            'technique_categories',
            'technique_library',
            'user_technique_bookmarks',
            'exercise_categories',
            'muscle_groups',
            'equipment',
            'exercises',
            'workout_exercises',
            'favorite_exercises',
            'workout_plans',
            'workout_plan_exercises'
        ]
        
        migrated_tables = []
        
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
                    
                    print(f"   📊 Found {len(rows)} rows")
                    
                    # Clear PostgreSQL table first
                    with postgres_engine.connect() as postgres_conn:
                        postgres_conn.execute(text(f'DELETE FROM {table_name}'))
                        postgres_conn.commit()
                    
                    # Insert data into PostgreSQL
                    with postgres_engine.connect() as postgres_conn:
                        # Create insert statement
                        columns_str = ', '.join(columns)
                        placeholders = ', '.join([f':{col}' for col in columns])
                        insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
                        
                        # Convert rows to dictionaries
                        data_dicts = []
                        for row in rows:
                            row_dict = {}
                            for i, col in enumerate(columns):
                                value = row[i]
                                # Handle JSON columns that might be stored as strings
                                if col in ['instructions', 'primary_muscles', 'secondary_muscles', 'equipment_needed', 'exercise_muscles', 'exercise_equipment'] and isinstance(value, str):
                                    try:
                                        # Try to parse as JSON, fallback to string
                                        json.loads(value)
                                    except:
                                        pass  # Keep as string
                                row_dict[col] = value
                            data_dicts.append(row_dict)
                        
                        # Execute batch insert
                        postgres_conn.execute(text(insert_sql), data_dicts)
                        postgres_conn.commit()
                    
                    print(f"   ✅ Successfully migrated {len(rows)} rows")
                    migrated_tables.append(table_name)
                    
                except Exception as e:
                    print(f"   ❌ Error migrating {table_name}: {str(e)}")
                    continue
        
        # Reset sequences for PostgreSQL auto-increment columns
        print(f"\n🔧 Resetting PostgreSQL sequences...")
        with postgres_engine.connect() as postgres_conn:
            for table in migrated_tables:
                try:
                    # Get the maximum ID from the table
                    result = postgres_conn.execute(text(f'SELECT MAX(id) FROM {table}'))
                    max_id = result.scalar()
                    
                    if max_id is not None:
                        # Reset the sequence
                        postgres_conn.execute(text(f'SELECT setval(pg_get_serial_sequence(\'{table}\', \'id\'), {max_id})'))
                        postgres_conn.commit()
                        print(f"   ✅ Reset sequence for {table} to {max_id}")
                except Exception as e:
                    print(f"   ⚠️ Could not reset sequence for {table}: {e}")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Migrated {len(migrated_tables)} tables: {', '.join(migrated_tables)}")
        print(f"\n💡 You can now:")
        print(f"   1. Update your .env to use PostgreSQL")
        print(f"   2. Restart your application")
        print(f"   3. Test that everything works")
        print(f"   4. Delete the SQLite file: dojotracker.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_data()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)