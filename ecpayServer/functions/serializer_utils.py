import json
from datetime import datetime

def serialize_parameter(value):
    if isinstance(value, datetime):
        return value.timestamp() * 1000  # Convert to milliseconds
    # Add other cases for serialization as needed
    return value

def serialize_parameter_data(parameter_data):
    serialized_data = {}
    for key, value in parameter_data.items():
        serialized_value = serialize_parameter(value)
        if serialized_value is not None:
            serialized_data[key] = serialized_value
    return json.dumps(serialized_data)

