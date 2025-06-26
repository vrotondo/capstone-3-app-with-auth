from datetime import datetime
from sqlalchemy import or_, and_
import logging

class TechniqueService:
    """Service class for managing technique library operations"""
    
    def __init__(self, db, models):
        self.db = db
        self.TechniqueLibrary = models['TechniqueLibrary']
        self.UserTechniqueBookmark = models['UserTechniqueBookmark']
        self.TechniqueCategory = models['TechniqueCategory']
        self.logger = logging.getLogger(__name__)
    
    def import_scraped_techniques(self, scraped_techniques):
        """Import scraped techniques into the database"""
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        print(f"📥 Importing {len(scraped_techniques)} scraped techniques...")
        
        for technique_data in scraped_techniques:
            try:
                # Check if technique already exists
                existing = self.TechniqueLibrary.query.filter_by(
                    name=technique_data['name'],
                    source_url=technique_data['source_url']
                ).first()
                
                if existing:
                    # Update existing technique if content has changed
                    if self._should_update_technique(existing, technique_data):
                        self._update_technique(existing, technique_data)
                        updated_count += 1
                        print(f"🔄 Updated: {technique_data['name']}")
                    else:
                        skipped_count += 1
                        print(f"⏭️ Skipped: {technique_data['name']} (no changes)")
                else:
                    # Create new technique
                    self._create_technique(technique_data)
                    imported_count += 1
                    print(f"✅ Imported: {technique_data['name']}")
                    
            except Exception as e:
                self.logger.error(f"Error importing technique {technique_data.get('name', 'Unknown')}: {str(e)}")
                print(f"❌ Error importing {technique_data.get('name', 'Unknown')}: {str(e)}")
        
        try:
            self.db.session.commit()
            print(f"\n📊 Import Summary:")
            print(f"   ✅ Imported: {imported_count}")
            print(f"   🔄 Updated: {updated_count}")
            print(f"   ⏭️ Skipped: {skipped_count}")
            
            return {
                'imported': imported_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'total': len(scraped_techniques)
            }
            
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"Database commit failed: {str(e)}")
            raise e
    
    def _should_update_technique(self, existing, new_data):
        """Check if existing technique should be updated with new data"""
        # Update if content has significantly changed
        fields_to_check = ['description', 'instructions', 'tips', 'variations']
        
        for field in fields_to_check:
            existing_value = getattr(existing, field) or ''
            new_value = new_data.get(field) or ''
            
            # If new content is significantly longer, update
            if len(new_value) > len(existing_value) * 1.2:
                return True
        
        return False
    
    def _create_technique(self, technique_data):
        """Create a new technique in the database"""
        # Clean and validate data
        cleaned_data = self._clean_technique_data(technique_data)
        
        technique = self.TechniqueLibrary(
            name=cleaned_data['name'],
            style=cleaned_data['style'],
            category=cleaned_data['category'],
            difficulty_level=cleaned_data['difficulty_level'],
            belt_level=cleaned_data['belt_level'],
            description=cleaned_data['description'],
            instructions=cleaned_data['instructions'],
            tips=cleaned_data['tips'],
            variations=cleaned_data['variations'],
            source_url=cleaned_data['source_url'],
            source_site=cleaned_data['source_site'],
            tags=cleaned_data['tags']
        )
        
        self.db.session.add(technique)
        return technique
    
    def _update_technique(self, existing, new_data):
        """Update existing technique with new data"""
        cleaned_data = self._clean_technique_data(new_data)
        
        # Update fields that may have changed
        existing.description = cleaned_data['description']
        existing.instructions = cleaned_data['instructions']
        existing.tips = cleaned_data['tips']
        existing.variations = cleaned_data['variations']
        existing.tags = cleaned_data['tags']
        existing.difficulty_level = cleaned_data['difficulty_level']
        existing.belt_level = cleaned_data['belt_level']
        existing.last_updated = datetime.utcnow()
        
        return existing
    
    def _clean_technique_data(self, data):
        """Clean and validate technique data"""
        cleaned = {
            'name': self._clean_text(data.get('name', '')),
            'style': self._clean_text(data.get('style', 'Unknown')),
            'category': self._clean_text(data.get('category')),
            'description': self._clean_long_text(data.get('description')),
            'instructions': self._clean_long_text(data.get('instructions')),
            'tips': self._clean_long_text(data.get('tips')),
            'variations': self._clean_long_text(data.get('variations')),
            'source_url': data.get('source_url', ''),
            'source_site': data.get('source_site', 'BlackBeltWiki'),
            'tags': self._clean_tags(data.get('tags', [])),
            'difficulty_level': self._validate_difficulty(data.get('difficulty_level')),
            'belt_level': self._clean_text(data.get('belt_level'))
        }
        
        return cleaned
    
    def _clean_text(self, text):
        """Clean short text fields"""
        if not text:
            return None
        
        cleaned = str(text).strip()
        # Remove excessive whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned if cleaned else None
    
    def _clean_long_text(self, text):
        """Clean long text fields like descriptions"""
        if not text:
            return None
        
        cleaned = str(text).strip()
        # Normalize line breaks
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
        
        # Limit length to prevent extremely long content
        max_length = 5000
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + '...'
        
        return cleaned if cleaned else None
    
    def _clean_tags(self, tags):
        """Clean and validate tags"""
        if not tags or not isinstance(tags, list):
            return []
        
        cleaned_tags = []
        for tag in tags:
            if isinstance(tag, str):
                clean_tag = self._clean_text(tag)
                if clean_tag and len(clean_tag) <= 50:  # Reasonable tag length
                    cleaned_tags.append(clean_tag)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in cleaned_tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        
        return unique_tags[:10]  # Limit to 10 tags
    
    def _validate_difficulty(self, difficulty):
        """Validate and normalize difficulty level"""
        if difficulty is None:
            return None
        
        try:
            level = int(difficulty)
            return max(1, min(10, level))  # Clamp between 1 and 10
        except (ValueError, TypeError):
            return None
    
    def search_techniques(self, query=None, style=None, category=None, difficulty=None, 
                         tags=None, limit=50, offset=0):
        """Search techniques with various filters"""
        try:
            techniques = self.TechniqueLibrary.search(
                query=query,
                style=style,
                category=category,
                difficulty=difficulty,
                tags=tags,
                limit=limit
            )
            
            return {
                'techniques': [t.to_dict(include_content=False) for t in techniques],
                'count': len(techniques),
                'has_more': len(techniques) == limit
            }
            
        except Exception as e:
            self.logger.error(f"Error searching techniques: {str(e)}")
            return {'techniques': [], 'count': 0, 'has_more': False}
    
    def get_technique_detail(self, technique_id, user_id=None):
        """Get detailed technique information"""
        try:
            technique = self.TechniqueLibrary.query.get(technique_id)
            if not technique:
                return None
            
            # Increment view count
            technique.increment_view_count()
            
            # Get technique data
            technique_data = technique.to_dict(include_content=True)
            
            # Add user-specific data if user is provided
            if user_id:
                bookmark = self.UserTechniqueBookmark.query.filter_by(
                    user_id=user_id,
                    technique_id=technique_id
                ).first()
                
                technique_data['user_bookmark'] = bookmark.to_dict(include_technique=False) if bookmark else None
                technique_data['is_bookmarked'] = bookmark is not None
            
            return technique_data
            
        except Exception as e:
            self.logger.error(f"Error getting technique detail: {str(e)}")
            return None
    
    def get_popular_techniques(self, limit=10):
        """Get most popular techniques by view count"""
        try:
            techniques = self.TechniqueLibrary.get_popular(limit=limit)
            return [t.to_dict(include_content=False) for t in techniques]
        except Exception as e:
            self.logger.error(f"Error getting popular techniques: {str(e)}")
            return []
    
    def get_techniques_by_style(self, style):
        """Get all techniques for a specific martial art style"""
        try:
            techniques = self.TechniqueLibrary.get_by_style(style)
            return [t.to_dict(include_content=False) for t in techniques]
        except Exception as e:
            self.logger.error(f"Error getting techniques by style: {str(e)}")
            return []
    
    def get_available_styles(self):
        """Get all available martial art styles"""
        try:
            styles = self.db.session.query(self.TechniqueLibrary.style).distinct().all()
            return [style[0] for style in styles if style[0]]
        except Exception as e:
            self.logger.error(f"Error getting available styles: {str(e)}")
            return []
    
    def get_available_categories(self):
        """Get all available technique categories"""
        try:
            categories = self.db.session.query(self.TechniqueLibrary.category).distinct().all()
            return [cat[0] for cat in categories if cat[0]]
        except Exception as e:
            self.logger.error(f"Error getting available categories: {str(e)}")
            return []
    
    def bookmark_technique(self, user_id, technique_id, notes=None):
        """Bookmark a technique for a user"""
        try:
            # Check if already bookmarked
            existing = self.UserTechniqueBookmark.query.filter_by(
                user_id=user_id,
                technique_id=technique_id
            ).first()
            
            if existing:
                return {'success': False, 'message': 'Technique already bookmarked'}
            
            # Create bookmark
            bookmark = self.UserTechniqueBookmark(
                user_id=user_id,
                technique_id=technique_id,
                personal_notes=notes
            )
            
            bookmark.save()
            
            # Update bookmark count on technique
            technique = self.TechniqueLibrary.query.get(technique_id)
            if technique:
                technique.bookmark_count += 1
                self.db.session.commit()
            
            return {
                'success': True,
                'bookmark': bookmark.to_dict(include_technique=False)
            }
            
        except Exception as e:
            self.logger.error(f"Error bookmarking technique: {str(e)}")
            self.db.session.rollback()
            return {'success': False, 'message': 'Failed to bookmark technique'}
    
    def remove_bookmark(self, user_id, technique_id):
        """Remove a technique bookmark"""
        try:
            bookmark = self.UserTechniqueBookmark.query.filter_by(
                user_id=user_id,
                technique_id=technique_id
            ).first()
            
            if not bookmark:
                return {'success': False, 'message': 'Bookmark not found'}
            
            bookmark.delete()
            
            # Update bookmark count on technique
            technique = self.TechniqueLibrary.query.get(technique_id)
            if technique and technique.bookmark_count > 0:
                technique.bookmark_count -= 1
                self.db.session.commit()
            
            return {'success': True, 'message': 'Bookmark removed'}
            
        except Exception as e:
            self.logger.error(f"Error removing bookmark: {str(e)}")
            self.db.session.rollback()
            return {'success': False, 'message': 'Failed to remove bookmark'}
    
    def get_user_bookmarks(self, user_id, limit=None):
        """Get all bookmarked techniques for a user"""
        try:
            bookmarks = self.UserTechniqueBookmark.get_user_bookmarks(user_id, limit=limit)
            return [bookmark.to_dict(include_technique=True) for bookmark in bookmarks]
        except Exception as e:
            self.logger.error(f"Error getting user bookmarks: {str(e)}")
            return []
    
    def update_technique_progress(self, user_id, technique_id, mastery_level=None, notes=None):
        """Update user's progress on a technique"""
        try:
            bookmark = self.UserTechniqueBookmark.query.filter_by(
                user_id=user_id,
                technique_id=technique_id
            ).first()
            
            if not bookmark:
                return {'success': False, 'message': 'Technique not bookmarked'}
            
            bookmark.update_practice(mastery_level=mastery_level, notes=notes)
            self.db.session.commit()
            
            return {
                'success': True,
                'bookmark': bookmark.to_dict(include_technique=False)
            }
            
        except Exception as e:
            self.logger.error(f"Error updating technique progress: {str(e)}")
            self.db.session.rollback()
            return {'success': False, 'message': 'Failed to update progress'}
    
    def get_technique_stats(self):
        """Get general statistics about the technique library"""
        try:
            total_techniques = self.TechniqueLibrary.query.count()
            total_styles = self.db.session.query(self.TechniqueLibrary.style).distinct().count()
            total_categories = self.db.session.query(self.TechniqueLibrary.category).distinct().count()
            total_bookmarks = self.UserTechniqueBookmark.query.count()
            
            return {
                'total_techniques': total_techniques,
                'total_styles': total_styles,
                'total_categories': total_categories,
                'total_bookmarks': total_bookmarks
            }
            
        except Exception as e:
            self.logger.error(f"Error getting technique stats: {str(e)}")
            return {
                'total_techniques': 0,
                'total_styles': 0,
                'total_categories': 0,
                'total_bookmarks': 0
            }