import asyncio
import json
from jsonschema import validate, ValidationError
from openai import OpenAI


class OpenAIClient:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = kwargs.get("model", "gpt-3.5-turbo")
        self.temperature = kwargs.get("temperature", 0)
        self.top_p = kwargs.get("top_p", 0)
        self.max_tokens = kwargs.get("max_tokens", 512)
        self.client = OpenAI()

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

    def create_payload(
        self,
        prompt=None,
        system_prompt=None,
        messages=None,
        schema=None,
        json_mode=True,
    ):
        if not messages:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
        if prompt:
            messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
        if not schema:
            return payload

        if json_mode:
            payload["messages"][-1][
                "content"
            ] += f"\nSCHEMA - {schema}\nReturn JSON following above schema."
            payload["response_format"] = {"type": "json_object"}
        else:
            payload["tools"] = [
                {"type": "function", "function": {"name": "func", "parameters": schema}}
            ]
            payload["tool_choice"] = {"type": "function", "function": {"name": "func"}}
        return payload, messages

    async def call(
        self,
        prompt=None,
        system_prompt=None,
        messages=None,
        schema=None,
        json_mode=False,
        attempts=3,
    ):
        """
        :param prompt:
        :param system_prompt:
        :param messages:
        :param schema:
        :param json_mode:
        :param attempts:
        :return:

        Validation checks:
            either prompt or messages must be filled
            if json_mode is true then schema cannot be None
        """
        if attempts == 0:
            messages.append({"role": "error", "content": "Failed to Adhere to JSON"})
            return messages

        payload, messages = self.create_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            messages=messages,
            schema=schema,
            json_mode=json_mode,
        )
        response = self.client.chat.completions.create(**payload)
        message = response.choices[0].message
        messages.append(dict(message))

        if not schema:
            return messages

        if json_mode:
            json_response = json.loads(message.content)
            success, error_message = self.validate_json(json_response, schema)
            if success:
                return messages
            else:
                return await self.call(
                    prompt=error_message,
                    messages=messages,
                    schema=schema,
                    json_mode=json_mode,
                    attempts=attempts - 1,
                )
        else:
            tool_call = message.tool_calls[0]
            json_response = json.loads(tool_call.function.arguments)
            success, error_message = self.validate_json(json_response, schema)
            if success:
                messages.append(
                    {"role": "assistant", "content": tool_call.function.arguments}
                )
                return messages
            else:
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": error_message,
                    }
                )
                return await self.call(
                    messages=messages,
                    schema=schema,
                    json_mode=json_mode,
                    attempts=attempts - 1,
                )


if __name__ == "__main__":
    client = OpenAIClient()
    system_prompt = "You are a helpful assistant!"
    prompt = "Dell retweet sentiment analysis!"
    schema = {
        "type": "object",
        "properties": {
            "chart_type": {
                "type": "string",
                "enum": ["Counter", "Table", "Column", "Bar", "Line", "Spline", "Pie"],
                "description": "The chart type name that can be used to plot the data for user query from the selected enums",
            },
            "name": {"type": "string", "description": "The title of the chart plot"},
            "description": {
                "type": "string",
                "description": "A brief description of what the chart intends to plot",
            },
        },
        "required": ["chart_type", "name", "description"],
    }
    messages = asyncio.run(
        client.call(
            prompt=prompt, system_prompt=system_prompt, schema=schema, json_mode=True
        )
    )
    print(messages)
