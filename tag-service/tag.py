from flask import request, jsonify, Blueprint
from common_packages.models.models import Calibration, Tag, CalibrationTag, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import datetime
from common_packages.logs.logging_config import setup_logger

log = setup_logger(__file__)

tag_routes = Blueprint('tag_routes', __name__)


@tag_routes.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "tag-service"})


@tag_routes.route('/internal-calibration/<int:calibration_id>/tags', methods=['POST'])
def add_calibration_to_tag(calibration_id):
    """Add a calibration to a tag"""
    data = request.get_json()
    tag_name = data.get('tag_name')

    log.info(f"Received request to add calibration {calibration_id} to tag '{tag_name}'")

    try:
        # Check if calibration exists
        calibration = Calibration.query.get(calibration_id)
        if calibration is None:
            log.warning(f"Calibration not found: {calibration_id}")
            return jsonify({
                "status": {
                    "code": 404,
                    "message": "Calibration not found"
                }
            }), 404

        # Find or create the tag
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            # Create new tag if it doesn't exist (tags are arbitrary strings)
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.flush()  # Get the tag ID before committing
            log.info(f"Created new tag: {tag_name}")

        # Check if this calibration-tag relationship already exists and is active
        existing_relationship = CalibrationTag.query.filter(
            and_(
                CalibrationTag.calibration_id == calibration_id,
                CalibrationTag.tag_id == tag.id,
                CalibrationTag.removed_at.is_(None)  # Only active relationships
            )
        ).first()

        if existing_relationship:
            log.info(f"Calibration {calibration_id} is already tagged with '{tag_name}'")
            return jsonify({
                "status": {
                    "code": 200,
                    "message": f"Calibration is already tagged with '{tag_name}'"
                }
            }), 200

        # Check if there's a previously removed relationship that can be reactivated
        removed_relationship = CalibrationTag.query.filter(
            and_(
                CalibrationTag.calibration_id == calibration_id,
                CalibrationTag.tag_id == tag.id,
                CalibrationTag.removed_at.is_not(None)  # Previously removed
            )
        ).first()

        if removed_relationship:
            # Reactivate the relationship
            removed_relationship.reactivate()
            removed_relationship.added_by = data.get('added_by', 'system')
            log.info(f"Reactivated calibration {calibration_id} tag relationship with '{tag_name}'")
        else:
            # Create new calibration-tag relationship
            calibration_tag = CalibrationTag(
                calibration_id=calibration_id,
                tag_id=tag.id,
                added_by=data.get('added_by', 'system')
            )
            db.session.add(calibration_tag)
            log.info(f"Created new calibration-tag relationship: {calibration_id} -> {tag_name}")

        db.session.commit()

        return jsonify({
            "status": {
                "code": 201,
                "message": f"Calibration successfully added to tag '{tag_name}'"
            },
            "data": {
                "calibration_id": calibration_id,
                "tag_name": tag_name,
                "tag_id": tag.id
            }
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        log.error(f"Database error adding calibration {calibration_id} to tag '{tag_name}': {str(e)}")
        return jsonify({
            "status": {
                "code": 400,
                "message": "Database error occurred",
                "error": str(e)
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        log.error(f"Error adding calibration {calibration_id} to tag '{tag_name}': {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500


@tag_routes.route('/internal-calibration/<int:calibration_id>/tags/<string:tag_name>', methods=['DELETE'])
def remove_calibration_from_tag(calibration_id, tag_name):
    """Remove a calibration from a tag (soft delete)"""
    log.info(f"Received request to remove calibration {calibration_id} from tag '{tag_name}'")

    try:
        # Check if calibration exists
        calibration = Calibration.query.get(calibration_id)
        if calibration is None:
            log.warning(f"Calibration not found: {calibration_id}")
            return jsonify({
                "status": {
                    "code": 404,
                    "message": "Calibration not found"
                }
            }), 404

        # Find the tag
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            log.warning(f"Tag not found: {tag_name}")
            return jsonify({
                "status": {
                    "code": 404,
                    "message": f"Tag '{tag_name}' not found"
                }
            }), 404

        # Find the active calibration-tag relationship
        calibration_tag = CalibrationTag.query.filter(
            and_(
                CalibrationTag.calibration_id == calibration_id,
                CalibrationTag.tag_id == tag.id,
                CalibrationTag.removed_at.is_(None)  # Only active relationships
            )
        ).first()

        if calibration_tag is None:
            # Calibration is not currently tagged with this tag - but return success (idempotent)
            log.info(f"Calibration {calibration_id} is not tagged with '{tag_name}' (idempotent operation)")
            return jsonify({
                "status": {
                    "code": 200,
                    "message": f"Calibration was not tagged with '{tag_name}' (no action needed)"
                }
            }), 200

        # Soft delete the relationship
        calibration_tag.soft_delete()
        db.session.commit()

        log.info(f"Successfully removed calibration {calibration_id} from tag '{tag_name}'")

        return jsonify({
            "status": {
                "code": 200,
                "message": f"Calibration successfully removed from tag '{tag_name}'"
            },
            "data": {
                "calibration_id": calibration_id,
                "tag_name": tag_name,
                "removed_at": datetime.utcnow().isoformat()
            }
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        log.error(f"Database error removing calibration {calibration_id} from tag '{tag_name}': {str(e)}")
        return jsonify({
            "status": {
                "code": 400,
                "message": "Database error occurred",
                "error": str(e)
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        log.error(f"Error removing calibration {calibration_id} from tag '{tag_name}': {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500


@tag_routes.route('/internal-calibration/<int:calibration_id>/tags', methods=['GET'])
def get_calibration_tags(calibration_id):
    """Get all tags currently associated with a calibration"""
    log.info(f"Received request to get tags for calibration {calibration_id}")

    try:
        # Check if calibration exists
        calibration = Calibration.query.get(calibration_id)
        if calibration is None:
            log.warning(f"Calibration not found: {calibration_id}")
            return jsonify({
                "status": {
                    "code": 404,
                    "message": "Calibration not found"
                }
            }), 404

        # Query for all active tags associated with this calibration
        active_tags_query = db.session.query(Tag, CalibrationTag).\
            join(CalibrationTag, Tag.id == CalibrationTag.tag_id).\
            filter(
                and_(
                    CalibrationTag.calibration_id == calibration_id,
                    CalibrationTag.removed_at.is_(None)  # Only active relationships
                )
            ).\
            order_by(CalibrationTag.added_at.desc())

        # Build response data
        tags_data = []
        for tag, calibration_tag in active_tags_query.all():
            tag_info = {
                "tag_id": tag.id,
                "tag_name": tag.name,
                "description": tag.description,
                "added_at": calibration_tag.added_at.isoformat() if calibration_tag.added_at else None,
                "added_by": calibration_tag.added_by
            }
            tags_data.append(tag_info)

        log.info(f"Found {len(tags_data)} active tags for calibration {calibration_id}")

        return jsonify({
            "status": {
                "code": 200,
                "message": "Success"
            },
            "data": {
                "calibration_id": calibration_id,
                "calibration_info": calibration.to_dict(),
                "tags": tags_data,
                "tag_count": len(tags_data)
            }
        }), 200

    except Exception as e:
        log.error(f"Error getting tags for calibration {calibration_id}: {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500


@tag_routes.route('/internal-tags', methods=['GET'])
def get_all_tags():
    """Get all tags in the system"""
    try:
        tags = Tag.query.order_by(Tag.name).all()
        tags_data = [tag.to_dict() for tag in tags]

        return jsonify({
            "status": {
                "code": 200,
                "message": "Success"
            },
            "data": {
                "tags": tags_data,
                "count": len(tags_data)
            }
        }), 200

    except Exception as e:
        log.error(f"Error getting all tags: {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500
