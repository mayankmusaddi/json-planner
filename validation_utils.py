from jsonschema import validate, ValidationError


class Validator:
    @staticmethod
    def validate_json(response, schema):
        success = True
        error_message = ""
        try:
            validate(instance=response, schema=schema)
        except ValidationError as e:
            success = False
            error = str(e).split("\n")[0]
            error_message = f"Response not adhering to schema:\n{error}"
        return success, error_message


if __name__ == "__main__":
    import json
    from fixtures import json_examples

    json_response = json.loads('{"chart_type": "Pie"}')
    schema = json_examples[0]["schema"]
    success, error_message = Validator.validate_json(json_response, schema)
    print(success, error_message)
