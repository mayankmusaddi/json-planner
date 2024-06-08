class JSONSchema:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def is_first_level(schema):
        if schema["type"] in ["array", "object"]:
            return False
        return True

    def is_reducible(self, schema):
        if self.is_first_level(schema):
            return True

        if schema["type"] == "object":
            if len(schema["properties"].keys()) > 1:
                return False
            sub_schema = list(schema["properties"].values())[0]
            return self.is_first_level(sub_schema)

        if schema["type"] == "array":
            return self.is_first_level(schema["items"])

    def first_level_prompt(self, schema, title=None, description=""):
        prompt = ""
        description = schema.get("description", description)
        if not title:
            title = "following"
        prompt += f"Specify the {title} - {description}\n"
        prompt += f"Respond with a {schema['type']}\n"
        if schema.get("enum"):
            prompt += f"Make sure to choose between {', '.join(schema['enum'])}"
        return prompt

    def schema_prompt(self, schema, title=None):
        if not self.is_reducible(schema):
            return
        if self.is_first_level(schema):
            return self.first_level_prompt(schema, title)
        description = schema.get("description", "")
        if schema["type"] == "object":
            title, sub_schema = list(schema["properties"].items())[0]
            return self.first_level_prompt(sub_schema, title, description)
        if schema["type"] == "array":
            sub_schema = schema["items"]
            min_items = schema.get("minItems")
            max_items = schema.get("maxItems")
            if min_items and max_items and min_items == max_items:
                prompt = f"Respond a list of comma separated {min_items} items specifying the following:\n"
            elif min_items and max_items:
                prompt = f"Respond a list of comma separated items at max {max_items} and at least {min_items} specifying the following:\n"
            elif min_items:
                prompt = f"Respond a list of comma separated at least {min_items} items specifying the following:\n"
            elif max_items:
                prompt = f"Respond a list of comma separated at max {max_items} items specifying the following:\n"
            prompt += self.first_level_prompt(sub_schema, title, description)
            return prompt


if __name__ == "__main__":
    json_schema = JSONSchema()
    schema = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "description": "List of items",
    }
    print(json_schema.schema_prompt(schema))
