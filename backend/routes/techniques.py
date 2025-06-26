from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

techniques_bp = Blueprint('techniques', __name__)

def get_current_user_id():
    """Get current user ID from JWT token and convert from string to int"""
    current_user_id_str = get_jwt_identity()
    return int(current_user_id_str) if current_user_id_str else None

def get_technique_service():
    """Get technique service instance"""
    from services.technique_service import TechniqueService
    from models.technique_library import create_technique_models
    
    db = current_app.extensions['sqlalchemy']
    TechniqueLibrary, UserTechniqueBookmark, TechniqueCategory = create_technique_models(db)
    
    models = {
        'TechniqueLibrary': TechniqueLibrary,
        'UserTechniqueBookmark': UserTechniqueBookmark,
        'TechniqueCategory': TechniqueCategory
    }
    
    return TechniqueService(db, models)

# Public Routes (no authentication required)

@techniques_bp.route('/search', methods=['GET'])
def search_techniques():
    """Search techniques in the library"""
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        style = request.args.get('style', '').strip()
        category = request.args.get('category', '').strip()
        difficulty = request.args.get('difficulty', type=int)
        tags = request.args.getlist('tags')
        limit = min(request.args.get('limit', 20, type=int), 100)  # Max 100
        offset = request.args.get('offset', 0, type=int)
        
        print(f"🔍 Searching techniques: q='{query}', style='{style}', category='{category}'")
        
        service = get_technique_service()
        result = service.search_techniques(
            query=query if query else None,
            style=style if style else None,
            category=category if category else None,
            difficulty=difficulty,
            tags=tags if tags else None,
            limit=limit,
            offset=offset
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Search techniques error: {str(e)}")
        return jsonify({'message': 'Failed to search techniques'}), 500

@techniques_bp.route('/<int:technique_id>', methods=['GET'])
def get_technique_detail(technique_id):
    """Get detailed information about a specific technique"""
    try:
        # Get user ID if authenticated
        user_id = None
        try:
            user_id = get_current_user_id()
        except:
            pass  # Not authenticated, continue without user data
        
        service = get_technique_service()
        technique = service.get_technique_detail(technique_id, user_id=user_id)
        
        if not technique:
            return jsonify({'message': 'Technique not found'}), 404
        
        return jsonify({
            'technique': technique,
            'message': 'Technique retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get technique detail error: {str(e)}")
        return jsonify({'message': 'Failed to get technique'}), 500

@techniques_bp.route('/popular', methods=['GET'])
def get_popular_techniques():
    """Get most popular techniques"""
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        service = get_technique_service()
        techniques = service.get_popular_techniques(limit=limit)
        
        return jsonify({
            'techniques': techniques,
            'count': len(techniques),
            'message': 'Popular techniques retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get popular techniques error: {str(e)}")
        return jsonify({'message': 'Failed to get popular techniques'}), 500

@techniques_bp.route('/styles', methods=['GET'])
def get_available_styles():
    """Get all available martial art styles"""
    try:
        service = get_technique_service()
        styles = service.get_available_styles()
        
        return jsonify({
            'styles': styles,
            'count': len(styles),
            'message': 'Styles retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get styles error: {str(e)}")
        return jsonify({'message': 'Failed to get styles'}), 500

@techniques_bp.route('/categories', methods=['GET'])
def get_available_categories():
    """Get all available technique categories"""
    try:
        service = get_technique_service()
        categories = service.get_available_categories()
        
        return jsonify({
            'categories': categories,
            'count': len(categories),
            'message': 'Categories retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get categories error: {str(e)}")
        return jsonify({'message': 'Failed to get categories'}), 500

@techniques_bp.route('/stats', methods=['GET'])
def get_technique_stats():
    """Get general statistics about the technique library"""
    try:
        service = get_technique_service()
        stats = service.get_technique_stats()
        
        return jsonify({
            'stats': stats,
            'message': 'Statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get technique stats error: {str(e)}")
        return jsonify({'message': 'Failed to get statistics'}), 500

# Authenticated Routes

@techniques_bp.route('/bookmarks', methods=['GET'])
@jwt_required()
def get_user_bookmarks():
    """Get user's bookmarked techniques"""
    try:
        user_id = get_current_user_id()
        limit = min(request.args.get('limit', 50, type=int), 100)
        
        service = get_technique_service()
        bookmarks = service.get_user_bookmarks(user_id, limit=limit)
        
        return jsonify({
            'bookmarks': bookmarks,
            'count': len(bookmarks),
            'message': 'Bookmarks retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user bookmarks error: {str(e)}")
        return jsonify({'message': 'Failed to get bookmarks'}), 500

@techniques_bp.route('/<int:technique_id>/bookmark', methods=['POST'])
@jwt_required()
def bookmark_technique(technique_id):
    """Bookmark a technique"""
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        notes = data.get('notes', '').strip() or None
        
        service = get_technique_service()
        result = service.bookmark_technique(user_id, technique_id, notes=notes)
        
        if result['success']:
            return jsonify({
                'bookmark': result['bookmark'],
                'message': 'Technique bookmarked successfully'
            }), 201
        else:
            return jsonify({'message': result['message']}), 400
        
    except Exception as e:
        current_app.logger.error(f"Bookmark technique error: {str(e)}")
        return jsonify({'message': 'Failed to bookmark technique'}), 500

@techniques_bp.route('/<int:technique_id>/bookmark', methods=['DELETE'])
@jwt_required()
def remove_bookmark(technique_id):
    """Remove a technique bookmark"""
    try:
        user_id = get_current_user_id()
        
        service = get_technique_service()
        result = service.remove_bookmark(user_id, technique_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'message': result['message']}), 400
        
    except Exception as e:
        current_app.logger.error(f"Remove bookmark error: {str(e)}")
        return jsonify({'message': 'Failed to remove bookmark'}), 500

@techniques_bp.route('/<int:technique_id>/progress', methods=['PUT'])
@jwt_required()
def update_technique_progress(technique_id):
    """Update user's progress on a technique"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        mastery_level = data.get('mastery_level')
        notes = data.get('notes', '').strip() or None
        
        # Validate mastery level
        if mastery_level is not None:
            if not isinstance(mastery_level, int) or mastery_level < 1 or mastery_level > 10:
                return jsonify({'message': 'Mastery level must be between 1 and 10'}), 400
        
        service = get_technique_service()
        result = service.update_technique_progress(
            user_id, technique_id, 
            mastery_level=mastery_level, 
            notes=notes
        )
        
        if result['success']:
            return jsonify({
                'bookmark': result['bookmark'],
                'message': 'Progress updated successfully'
            }), 200
        else:
            return jsonify({'message': result['message']}), 400
        
    except Exception as e:
        current_app.logger.error(f"Update technique progress error: {str(e)}")
        return jsonify({'message': 'Failed to update progress'}), 500

# Admin Routes

@techniques_bp.route('/import', methods=['POST'])
@jwt_required()
def import_techniques():
    """Import techniques from external sources (admin only)"""
    try:
        user_id = get_current_user_id()
        
        # TODO: Add admin check
        # For now, allow any authenticated user for testing
        
        data = request.get_json()
        if not data or 'source' not in data:
            return jsonify({'message': 'Source parameter required'}), 400
        
        source = data['source'].lower()
        max_techniques = min(data.get('max_techniques', 20), 100)  # Limit for safety
        
        if source == 'blackbeltwiki':
            from services.blackbelt_scraper import BlackBeltWikiScraper
            
            print(f"🕷️ Starting BlackBeltWiki scraping (max: {max_techniques})")
            
            scraper = BlackBeltWikiScraper(delay=2)  # Respectful delay
            scraped_techniques = scraper.scrape_techniques(max_techniques=max_techniques)
            
            if not scraped_techniques:
                return jsonify({'message': 'No techniques found to import'}), 404
            
            service = get_technique_service()
            result = service.import_scraped_techniques(scraped_techniques)
            
            return jsonify({
                'import_result': result,
                'message': f'Import completed: {result["imported"]} new, {result["updated"]} updated'
            }), 200
            
        else:
            return jsonify({'message': f'Unknown source: {source}'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Import techniques error: {str(e)}")
        return jsonify({'message': f'Import failed: {str(e)}'}), 500

# Test Routes

@techniques_bp.route('/test', methods=['GET'])
def test_techniques():
    """Test endpoint for technique system"""
    return jsonify({
        'message': 'Technique library system is working',
        'timestamp': str(datetime.utcnow()),
        'endpoints': {
            'search': 'GET /api/techniques/search',
            'detail': 'GET /api/techniques/<id>',
            'popular': 'GET /api/techniques/popular',
            'styles': 'GET /api/techniques/styles',
            'categories': 'GET /api/techniques/categories',
            'bookmarks': 'GET /api/techniques/bookmarks (auth)',
            'bookmark': 'POST /api/techniques/<id>/bookmark (auth)',
            'progress': 'PUT /api/techniques/<id>/progress (auth)',
            'import': 'POST /api/techniques/import (auth)'
        }
    }), 200

@techniques_bp.route('/test-scraper', methods=['POST'])
def test_scraper():
    """Test the BlackBeltWiki scraper"""
    try:
        from services.blackbelt_scraper import BlackBeltWikiScraper
        
        print("🧪 Testing BlackBeltWiki scraper...")
        
        scraper = BlackBeltWikiScraper(delay=1)  # Faster for testing
        techniques = scraper.scrape_techniques(max_techniques=3)
        
        return jsonify({
            'message': 'Scraper test completed',
            'techniques_found': len(techniques),
            'sample_techniques': [
                {
                    'name': t['name'],
                    'style': t['style'],
                    'description_length': len(t.get('description', '') or ''),
                    'source_url': t['source_url']
                }
                for t in techniques[:3]
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Test scraper error: {str(e)}")
        return jsonify({'message': f'Scraper test failed: {str(e)}'}), 500