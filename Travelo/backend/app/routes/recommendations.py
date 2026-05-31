from flask import Blueprint, jsonify
import json
import os
import logging
from pathlib import Path
from app.utils.decorators import token_required

logger = logging.getLogger(__name__)
recommendations_bp = Blueprint('recommendations', __name__)

def load_destinations():
    """Load destinations from JSON file with proper path handling"""
    try:
        # Get the absolute path to destinations.json
        # It should be in the same directory as run.py
        base_dir = Path(__file__).resolve().parent.parent.parent
        file_path = base_dir / 'destinations.json'
        
        if not file_path.exists():
            logger.error(f"destinations.json not found at {file_path}")
            raise FileNotFoundError(f"Destinations file not found at {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            destinations = json.load(f)
        
        if not isinstance(destinations, list):
            logger.error("destinations.json must contain a list of destinations")
            raise ValueError("destinations.json must contain a list of destinations")
        
        logger.info(f"Loaded {len(destinations)} destinations from {file_path}")
        return destinations
        
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in destinations.json: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading destinations: {str(e)}")
        raise

@recommendations_bp.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user_id):
    """Get personalized destination recommendations based on user preferences"""
    try:
        # Import inside function to avoid circular import
        from app.models.models import UserPreference, TravelHistory
        
        # Get user preferences
        prefs = UserPreference.query.filter_by(user_id=int(current_user_id)).first()
        if not prefs:
            return jsonify({"error": "Please set your preferences first"}), 400
        
        # Load destinations
        try:
            destinations = load_destinations()
        except Exception as e:
            logger.error(f"Failed to load destinations: {str(e)}")
            return jsonify({"error": "Unable to load recommendations at this time"}), 500
        
        # Get user's travel history for liked destinations
        history = TravelHistory.query.filter_by(user_id=int(current_user_id)).all()
        liked_dest_names = [h.destination_name for h in history if h.user_rating and h.user_rating >= 4]
        
        scored = []
        
        # Score each destination
        for dest in destinations:
            # Validate destination structure
            if not isinstance(dest, dict):
                logger.warning(f"Skipping invalid destination: {dest}")
                continue
            
            # Check required fields
            if 'name' not in dest:
                logger.warning("Destination missing 'name' field")
                continue
            
            try:
                score = 0
                dest_name = dest.get('name', 'Unknown')
                
                # Score based on type preference (weight: 40)
                if prefs.preferred_destination_type:
                    if dest.get('type', '').lower() == prefs.preferred_destination_type.lower():
                        score += 40
                
                # Score based on travel style preference (weight: 30)
                if prefs.travel_style:
                    if dest.get('style', '').lower() == prefs.travel_style.lower():
                        score += 30
                
                # Score based on budget (weight: 20)
                if prefs.max_budget:
                    avg_cost = dest.get('avg_cost_per_day')
                    if isinstance(avg_cost, (int, float)):
                        # Allow 25% buffer on budget
                        if avg_cost <= prefs.max_budget * 1.25:
                            score += 20
                
                # Score based on region preference (weight: 15)
                if prefs.preferred_region:
                    region = str(dest.get('region', '')).lower()
                    if prefs.preferred_region.lower() in region:
                        score += 15
                
                # Score based on travel history (weight: 25)
                if dest_name in liked_dest_names:
                    score += 25
                
                # Add destination with score to results
                scored.append({
                    **dest,
                    "match_score": min(score, 100)  # Cap score at 100
                })
                
            except Exception as e:
                logger.error(f"Error scoring destination {dest.get('name', 'Unknown')}: {str(e)}")
                continue
        
        # Sort by match score in descending order
        scored.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Return top 8 recommendations
        recommendations = scored[:8]
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {current_user_id}")
        
        return jsonify({
            "recommendations": recommendations,
            "total_scored": len(scored),
            "total_available": len(destinations),
            "message": "Recommendations generated successfully"
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in get_recommendations: {str(e)}")
        return jsonify({"error": "An error occurred while generating recommendations"}), 500


@recommendations_bp.route('/destinations/count', methods=['GET'])
def get_destinations_count():
    """Get total number of available destinations"""
    try:
        destinations = load_destinations()
        return jsonify({
            "total_destinations": len(destinations),
            "message": "Successfully retrieved destination count"
        }), 200
    except Exception as e:
        logger.error(f"Error getting destination count: {str(e)}")
        return jsonify({"error": "Unable to retrieve destination information"}), 500