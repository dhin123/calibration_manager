import json
import os
import jsonschema


def validate_schema(to_validate, schema):
    schema_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'schemas', schema)
    print("Schema", schema_file_path)
    with open(schema_file_path, 'r') as file:
        schema = json.load(file)

    try:
        # Validate the payload against the schema
        jsonschema.validate(instance=to_validate, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        # If validation fails, return the error message
        return False
    return True
