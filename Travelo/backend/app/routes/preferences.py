from flask import Blueprint, request, jsonify
from app import db
from app.utils.decorators import token_required
import logging

logger = logging.getLogger(__name__)
preferences_bp = Blueprint('preferences', __name__)

# Import model inside function to avoid circular import
@preferences_bp.route('/preferences', methods=['GET'])
@token_required
def get_preferences(current_user_id):
    """Get user's travel preferences"""
    try:
        from app.models.models import UserPreference
        
        user_id = int(current_user_id)
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        
        if not pref:
            return jsonify({"error": "Preferences not found. Please create preferences first"}), 404
        
        return jsonify({
            "user_id": user_id,
            "preferred_destination_type": pref.preferred_destination_type,
            "max_budget": pref.max_budget,
            "travel_style": pref.travel_style,
            "preferred_region": pref.preferred_region,
            "message": "Preferences retrieved successfully"
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        logger.error(f"Error retrieving preferences: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving preferences"}), 500


@preferences_bp.route('/preferences', methods=['PUT'])
@token_required
def update_preferences(current_user_id):
    """Update user's travel preferences"""
    try:
        from app.models.models import UserPreference
        
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
        
        user_id = int(current_user_id)
        
        # Validate and type-convert incoming data
        validated_data = {}
        
        # Validate preferred_destination_type
        if 'preferred_destination_type' in data:
            dest_type = data.get('preferred_destination_type')
            if dest_type and not isinstance(dest_type, str):
                return jsonify({"error": "preferred_destination_type must be a string"}), 400
            validated_data['preferred_destination_type'] = dest_type
        
        # Validate max_budget
        if 'max_budget' in data:
            try:
                max_budget = data.get('max_budget')
                if max_budget is not None:
                    max_budget = int(max_budget)
                    if max_budget < 0:
                        return jsonify({"error": "max_budget must be a positive number"}), 400
                validated_data['max_budget'] = max_budget
            except (ValueError, TypeError):
                return jsonify({"error": "max_budget must be an integer"}), 400
        
        # Validate travel_style
        if 'travel_style' in data:
            travel_style = data.get('travel_style')
            if travel_style and not isinstance(travel_style, str):
                return jsonify({"error": "travel_style must be a string"}), 400
            validated_data['travel_style'] = travel_style
        
        # Validate preferred_region
        if 'preferred_region' in data:
            region = data.get('preferred_region')
            if region and not isinstance(region, str):
                return jsonify({"error": "preferred_region must be a string"}), 400
            validated_data['preferred_region'] = region
        
        # Get or create preferences
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        
        if not pref:
            pref = UserPreference(user_id=user_id)
            db.session.add(pref)
        
        # Update only provided fields
        for key, value in validated_data.items():
            setattr(pref, key, value)
        
        db.session.commit()
        
        logger.info(f"Updated preferences for user {user_id}")
        
        return jsonify({
            "message": "Preferences updated successfully",
            "user_id": user_id,
            "preferences": {
                "preferred_destination_type": pref.preferred_destination_type,
                "max_budget": pref.max_budget,
                "travel_style": pref.travel_style,
                "preferred_region": pref.preferred_region
            }
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({"error": "An error occurred while updating preferences"}), 500


@preferences_bp.route('/preferences', methods=['DELETE'])
@token_required
def delete_preferences(current_user_id):
    """Reset user preferences to defaults"""
    try:
        from app.models.models import UserPreference
        
        user_id = int(current_user_id)
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        
        if not pref:
            return jsonify({"error": "Preferences not found"}), 404
        
        # Reset to defaults instead of deleting
        pref.preferred_destination_type = None
        pref.max_budget = 100
        pref.travel_style = None
        pref.preferred_region = None
        
        db.session.commit()
        
        logger.info(f"Reset preferences for user {user_id}")
        
        return jsonify({"message": "Preferences reset to defaults"}), 200
        
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting preferences: {str(e)}")
        return jsonify({"error": "An error occurred while resetting preferences"}), 500