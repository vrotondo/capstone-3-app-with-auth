from datetime import datetime
from sqlalchemy import text

def create_technique_models(db):
    """Create technique library models with the provided db instance"""
    
    class TechniqueLibrary(db.Model):
        __tablename__ = 'technique_library'
        __table_args__ = {'extend_existing': True}  # Allow table redefinition
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False, index=True)
        style = db.Column(db.String(100), nullable=False, index=True)
        category = db.Column(db.String(100), nullable=True)  # kicks, punches, throws, etc.
        difficulty_level = db.Column(db.Integer, nullable=True)  # 1-10 scale
        belt_level = db.Column(db.String(50), nullable=True)  # White, Yellow, etc.
        
        # Content from BlackBeltWiki
        description = db.Column(db.Text, nullable=True)
        instructions = db.Column(db.Text, nullable=True)
        tips = db.Column(db.Text, nullable=True)
        variations = db.Column(db.Text, nullable=True)
        
        # Metadata
        source_url = db.Column(db.String(500), nullable=True)
        source_site = db.Column(db.String(100), default='BlackBeltWiki')
        tags = db.Column(db.JSON, nullable=True)  # List of tags
        scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Usage tracking
        view_count = db.Column(db.Integer, default=0)
        bookmark_count = db.Column(db.Integer, default=0)
        
        def __init__(self, name, style, **kwargs):
            self.name = name
            self.style = style
            self.category = kwargs.get('category')
            self.difficulty_level = kwargs.get('difficulty_level')
            self.belt_level = kwargs.get('belt_level')
            self.description = kwargs.get('description')
            self.instructions = kwargs.get('instructions')
            self.tips = kwargs.get('tips')
            self.variations = kwargs.get('variations')
            self.source_url = kwargs.get('source_url')
            self.source_site = kwargs.get('source_site', 'BlackBeltWiki')
            self.tags = kwargs.get('tags', [])
        
        def increment_view_count(self):
            """Increment view count"""
            self.view_count += 1
            db.session.commit()
        
        def to_dict(self, include_content=True):
            """Convert technique to dictionary"""
            data = {
                'id': self.id,
                'name': self.name,
                'style': self.style,
                'category': self.category,
                'difficulty_level': self.difficulty_level,
                'belt_level': self.belt_level,
                'source_url': self.source_url,
                'source_site': self.source_site,
                'tags': self.tags or [],
                'view_count': self.view_count,
                'bookmark_count': self.bookmark_count,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None
            }
            
            if include_content:
                data.update({
                    'description': self.description,
                    'instructions': self.instructions,
                    'tips': self.tips,
                    'variations': self.variations
                })
            
            return data
        
        def save(self):
            """Save technique to database"""
            db.session.add(self)
            db.session.commit()
        
        @staticmethod
        def search(query=None, style=None, category=None, difficulty=None, tags=None, limit=50):
            """Search techniques with filters"""
            filters = []
            
            if query:
                filters.append(db.or_(
                    TechniqueLibrary.name.ilike(f'%{query}%'),
                    TechniqueLibrary.description.ilike(f'%{query}%'),
                    TechniqueLibrary.instructions.ilike(f'%{query}%')
                ))
            
            if style:
                filters.append(TechniqueLibrary.style.ilike(f'%{style}%'))
            
            if category:
                filters.append(TechniqueLibrary.category.ilike(f'%{category}%'))
            
            if difficulty:
                filters.append(TechniqueLibrary.difficulty_level == difficulty)
            
            if tags:
                for tag in tags:
                    filters.append(TechniqueLibrary.tags.contains([tag]))
            
            query_obj = TechniqueLibrary.query
            if filters:
                query_obj = query_obj.filter(db.and_(*filters))
            
            return query_obj.order_by(TechniqueLibrary.name).limit(limit).all()
        
        @staticmethod
        def get_by_style(style):
            """Get all techniques for a specific martial art style"""
            return TechniqueLibrary.query.filter_by(style=style).order_by(TechniqueLibrary.name).all()
        
        @staticmethod
        def get_popular(limit=10):
            """Get most popular techniques by view count"""
            return TechniqueLibrary.query.order_by(TechniqueLibrary.view_count.desc()).limit(limit).all()
        
        def __repr__(self):
            return f'<TechniqueLibrary {self.name} ({self.style})>'

    class UserTechniqueBookmark(db.Model):
        __tablename__ = 'user_technique_bookmarks'
        __table_args__ = (
            db.UniqueConstraint('user_id', 'technique_id', name='unique_user_technique_bookmark'),
            {'extend_existing': True}  # Allow table redefinition
        )
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        technique_id = db.Column(db.Integer, db.ForeignKey('technique_library.id'), nullable=False)
        
        # User's personal notes and progress
        personal_notes = db.Column(db.Text, nullable=True)
        practice_count = db.Column(db.Integer, default=0)
        mastery_level = db.Column(db.Integer, default=1)  # 1-10 scale
        last_practiced = db.Column(db.Date, nullable=True)
        
        # Metadata
        bookmarked_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Ensure unique bookmark per user per technique
        # __table_args__ = (db.UniqueConstraint('user_id', 'technique_id', name='unique_user_technique_bookmark'),)
        # Moved to __table_args__ above
        
        # Relationships
        technique = db.relationship('TechniqueLibrary', backref='user_bookmarks')
        
        def __init__(self, user_id, technique_id, **kwargs):
            self.user_id = user_id
            self.technique_id = technique_id
            self.personal_notes = kwargs.get('personal_notes')
            self.mastery_level = kwargs.get('mastery_level', 1)
        
        def update_practice(self, mastery_level=None, notes=None):
            """Update practice information"""
            self.practice_count += 1
            self.last_practiced = datetime.utcnow().date()
            
            if mastery_level:
                self.mastery_level = mastery_level
                
            if notes:
                self.personal_notes = notes
                
            self.updated_at = datetime.utcnow()
        
        def to_dict(self, include_technique=True):
            """Convert bookmark to dictionary"""
            data = {
                'id': self.id,
                'user_id': self.user_id,
                'technique_id': self.technique_id,
                'personal_notes': self.personal_notes,
                'practice_count': self.practice_count,
                'mastery_level': self.mastery_level,
                'last_practiced': self.last_practiced.isoformat() if self.last_practiced else None,
                'bookmarked_at': self.bookmarked_at.isoformat() if self.bookmarked_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            
            if include_technique and self.technique:
                data['technique'] = self.technique.to_dict(include_content=False)
            
            return data
        
        def save(self):
            """Save bookmark to database"""
            db.session.add(self)
            db.session.commit()
        
        def delete(self):
            """Delete bookmark from database"""
            db.session.delete(self)
            db.session.commit()
        
        @staticmethod
        def get_user_bookmarks(user_id, limit=None):
            """Get all bookmarks for a user"""
            query = UserTechniqueBookmark.query.filter_by(user_id=user_id).order_by(
                UserTechniqueBookmark.updated_at.desc()
            )
            if limit:
                query = query.limit(limit)
            return query.all()
        
        @staticmethod
        def is_bookmarked(user_id, technique_id):
            """Check if technique is bookmarked by user"""
            return UserTechniqueBookmark.query.filter_by(
                user_id=user_id, 
                technique_id=technique_id
            ).first() is not None
        
        def __repr__(self):
            return f'<UserTechniqueBookmark User:{self.user_id} Technique:{self.technique_id}>'

    class TechniqueCategory(db.Model):
        __tablename__ = 'technique_categories'
        __table_args__ = {'extend_existing': True}  # Allow table redefinition
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        description = db.Column(db.Text, nullable=True)
        parent_category_id = db.Column(db.Integer, db.ForeignKey('technique_categories.id'), nullable=True)
        
        # Self-referential relationship for subcategories
        subcategories = db.relationship('TechniqueCategory', backref=db.backref('parent', remote_side=[id]))
        
        def __init__(self, name, description=None, parent_category_id=None):
            self.name = name
            self.description = description
            self.parent_category_id = parent_category_id
        
        def to_dict(self, include_subcategories=False):
            """Convert category to dictionary"""
            data = {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'parent_category_id': self.parent_category_id
            }
            
            if include_subcategories:
                data['subcategories'] = [sub.to_dict() for sub in self.subcategories]
            
            return data
        
        def save(self):
            """Save category to database"""
            db.session.add(self)
            db.session.commit()
        
        @staticmethod
        def get_root_categories():
            """Get all root categories (no parent)"""
            return TechniqueCategory.query.filter_by(parent_category_id=None).all()
        
        def __repr__(self):
            return f'<TechniqueCategory {self.name}>'

    return TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory