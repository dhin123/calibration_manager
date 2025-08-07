CALIBRATION_SCHEMA: str = 'create_calibration.json'
ADD_TAG_SCHEMA: str = 'add_or_delete_calibration_to_tag.json'
FILTER_CALIBRATIONS_SCHEMA: str = 'filter_calibration.json'

# Common calibration types (for reference/validation)
CALIBRATION_TYPES = [
    "offset",
    "gain",
    "temperature",
    "pressure",
    "voltage",
    "current",
    "frequency",
    "phase"
]

# API Response status codes and messages
STATUS_CODES = {
    "SUCCESS": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "NOT_FOUND": 404,
    "INTERNAL_ERROR": 500
}

STATUS_MESSAGES = {
    200: "Success",
    201: "Created successfully",
    400: "Bad request",
    404: "Not found",
    500: "Internal server error"
}
