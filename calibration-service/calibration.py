from flask import request, jsonify, Blueprint
from common_packages.models.models import Calibration, Tag, CalibrationTag, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import datetime
import random
from common_packages.utils.id_generator import SnowflakeIdGenerator
from common_packages.logs.logging_config import setup_logger

log = setup_logger(__file__)

calibration_routes = Blueprint('calibration_routes', __name__)


@calibration_routes.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "calibration-service"})


@calibration_routes.route('/internal-calibration', methods=['POST'])
def create_calibration():
    """Create a new calibration"""
    data = request.get_json()
    log.info(f"Received request to create calibration with: {data}")

    try:
        # Generate unique ID using Snowflake pattern
        id_generator = SnowflakeIdGenerator(
            worker_id=random.randint(0, 4),
            datacenter_id=random.randint(0, 4)
        )

        # Create new calibration
        new_calibration = Calibration(
            id=id_generator.generate(),
            calibration_type=data['calibration_type'].lower(),
            value=data['value'],
            username=data['username'],
            timestamp=datetime.utcnow()
        )

        calibration_id = new_calibration.id
        log.info(f"Created new calibration with id: {calibration_id}")

        db.session.add(new_calibration)
        db.session.commit()

        return jsonify({
            "status": {
                "code": 201,
                "message": "Calibration created successfully!",
                "calibration_id": calibration_id
            },
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        log.error(f"Error occurred while adding new calibration to the database: {str(e)}")
        return jsonify({
            "status": {
                "code": 400,
                "message": "Database error occurred",
                "error": str(e)
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        log.error(f"Unexpected error creating calibration: {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500


@calibration_routes.route('/internal-calibrations', methods=['GET'])
def get_calibrations():
    """Retrieve calibrations with filtering support"""
    try:
        # Extract query parameters
        username = request.args.get('username')
        calibration_type = request.args.get('calibration_type')
        tag_name = request.args.get('tag_name')
        tag_at_time = request.args.get('tag_at_time')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        log.info(f"Filtering calibrations with parameters: username={username}, "
                 f"type={calibration_type}, tag={tag_name}, dates={start_date}-{end_date}, tag_at_time={tag_at_time}")

        # Start with base query
        query = Calibration.query

        # Apply filters
        if username:
            query = query.filter(Calibration.username == username)

        if calibration_type:
            query = query.filter(Calibration.calibration_type == calibration_type.lower())

        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Calibration.timestamp >= start_dt)
            except ValueError:
                log.warning(f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Calibration.timestamp <= end_dt)
            except ValueError:
                log.warning(f"Invalid end_date format: {end_date}")

        # Tag filtering with historical support (direct JOIN on Tag.name)
        if tag_name:
            if tag_at_time:
                # HISTORICAL: What HAD this tag at specific time
                try:
                    at_time = datetime.fromisoformat(tag_at_time.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        "status": {"code": 400, "message": "Invalid tag_at_time format"}
                    }), 400

                query = (
                    query
                    .join(CalibrationTag, Calibration.id == CalibrationTag.calibration_id)
                    .join(Tag, Tag.id == CalibrationTag.tag_id)
                    .filter(
                        Tag.name == tag_name,
                        CalibrationTag.added_at <= at_time,
                        or_(
                            CalibrationTag.removed_at.is_(None),
                            CalibrationTag.removed_at > at_time
                        )
                    )
                )
            else:
                # CURRENT: What has this tag NOW
                query = (
                    query
                    .join(CalibrationTag, Calibration.id == CalibrationTag.calibration_id)
                    .join(Tag, Tag.id == CalibrationTag.tag_id)
                    .filter(
                        Tag.name == tag_name,
                        CalibrationTag.removed_at.is_(None)
                    )
                )

        # Apply pagination
        total_count = query.count()
        calibrations = query.order_by(Calibration.timestamp.desc()).paginate(
            page=page, per_page=limit, error_out=False
        ).items

        # Convert to dict
        calibrations_dict = [calibration.to_dict() for calibration in calibrations]

        return jsonify({
            "status": {
                "code": 200,
                "message": "Success"
            },
            "data": {
                "calibrations": calibrations_dict,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            }
        }), 200

    except Exception as e:
        log.error(f"Error retrieving calibrations: {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500


@calibration_routes.route('/internal-calibration/<int:calibration_id>', methods=['GET'])
def get_calibration_by_id(calibration_id):
    """Get a specific calibration by ID"""
    try:
        log.info(f"Retrieving calibration with id: {calibration_id}")

        calibration = Calibration.query.get(calibration_id)

        if calibration is None:
            log.warning(f"Calibration not found: {calibration_id}")
            return jsonify({
                "status": {
                    "code": 404,
                    "message": "Calibration not found"
                }
            }), 404

        return jsonify({
            "status": {
                "code": 200,
                "message": "Success"
            },
            "data": calibration.to_dict()
        }), 200

    except Exception as e:
        log.error(f"Error retrieving calibration {calibration_id}: {str(e)}")
        return jsonify({
            "status": {
                "code": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        }), 500
