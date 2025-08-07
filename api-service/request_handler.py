"""
request_handler validates the schema of incoming requests and routes them to appropriate services

"""

from flask import Blueprint, jsonify, request
import requests
from common_packages.constants.constants import CALIBRATION_SCHEMA, ADD_TAG_SCHEMA
from common_packages.utils.schema_validator import validate_schema
from common_packages.logs.logging_config import setup_logger

routes = Blueprint('routes', __name__)
log = setup_logger(__file__)


# Health check endpoints
@routes.route('/', methods=['GET'])
def hello():
    log.info("GET request received at '/' endpoint")
    return jsonify({"status": "Calibration API Gateway is running"})


@routes.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "calibration-api-service"})


@routes.route('/api/v1/calibrations', methods=['POST'])
def create_calibration():
    data = request.get_json()
    log.info(f"Received request to create calibration with: {data}")

    if validate_schema(data, CALIBRATION_SCHEMA):
        response = requests.post('http://calibration-service:5001/internal-calibration', json=data)
        log.info(f"Routed calibration creation request to calibration service")
        return response.content, response.status_code
    else:
        log.warning(f"Invalid schema for calibration creation: {data}")
        return jsonify({
            "status": {
                "code": 400,
                "message": "Invalid schema. Please use the correct schema for calibration creation"
            }
        }), 400


@routes.route('/api/v1/calibrations', methods=['GET'])
def get_calibrations():
    # Extract query parameters for the 4 filter types mentioned in challenge
    filters = {
        'username': request.args.get('username'),                # Filter by USER
        'calibration_type': request.args.get('calibration_type'), # Filter by TYPE
        'tag_name': request.args.get('tag_name'),                # Filter by TAG
        'tag_at_time': request.args.get('tag_at_time'),
        'start_date': request.args.get('start_date'),            # Filter by TIME
        'end_date': request.args.get('end_date'),                # Filter by TIME
        'page': request.args.get('page', 1, type=int),
        'limit': request.args.get('limit', 20, type=int)
    }

    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    log.info(f"Received request to get calibrations with filters: {filters}")

    response = requests.get('http://calibration-service:5001/internal-calibrations', params=filters)
    log.info(f"Routed get calibrations request to calibration service")
    return response.content, response.status_code


# USE CASE 2: Add a Calibration to a tag
@routes.route('/api/v1/calibrations/<int:calibration_id>/tags', methods=['POST'])
def add_calibration_to_tag(calibration_id):
    data = request.get_json()
    log.info(f"Received request to add calibration {calibration_id} to tag: {data}")

    if validate_schema(data, ADD_TAG_SCHEMA):
        response = requests.post(
            f'http://tag-service:5002/internal-calibration/{calibration_id}/tags',
            json=data
        )
        log.info(f"Routed add-to-tag request to tag service")
        return response.content, response.status_code
    else:
        log.warning(f"Invalid schema for adding calibration to tag: {data}")
        return jsonify({
            "status": {
                "code": 400,
                "message": "Invalid schema. Please use the correct schema for adding calibration to tag"
            }
        }), 400


@routes.route('/api/v1/calibrations/<int:calibration_id>/tags/<string:tag_name>', methods=['DELETE'])
def remove_calibration_from_tag(calibration_id, tag_name):
    log.info(f"Received request to remove calibration {calibration_id} from tag {tag_name}")

    response = requests.delete(
        f'http://tag-service:5002/internal-calibration/{calibration_id}/tags/{tag_name}'
    )
    log.info(f"Routed remove-from-tag request to tag service")
    return response.content, response.status_code


@routes.route('/api/v1/calibrations/<int:calibration_id>/tags', methods=['GET'])
def get_calibration_tags(calibration_id):
    log.info(f"Received request to get tags for calibration {calibration_id}")

    response = requests.get(f'http://tag-service:5002/internal-calibration/{calibration_id}/tags')
    log.info(f"Routed get calibration tags request to tag service")
    return response.content, response.status_code


@routes.route('/api/v1/tags', methods=['GET'])
def get_all_tags():
    log.info("Received request to get all tags")
    response = requests.get('http://tag-service:5002/internal-tags')
    log.info(f"Routed get all tags request to tag service")
    return response.content, response.status_code
