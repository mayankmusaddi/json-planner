import json
from validation_utils import Validator
import logging
from openai import OpenAI
from schema import JSONSchema

JSON_MODE = "json_mode"
TOOL_CALL = "tool_call"
SIMPLIFY = "simplify"


class OpenAIClient:
    def __init__(self, *args, **kwargs):
        self.model = kwargs.get("model", "gpt-3.5-turbo")
        self.temperature = kwargs.get("temperature", 0)
        self.top_p = kwargs.get("top_p", 0)
        self.max_tokens = kwargs.get("max_tokens", 512)
        self.client = OpenAI()

    def create_payload(
        self,
        prompt=None,
        system_prompt=None,
        messages=None,
        schema=None,
        mode=JSON_MODE,
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
            return payload, messages

        if mode == JSON_MODE:
            payload["messages"][-1][
                "content"
            ] += f"\nSCHEMA - {schema}\nReturn JSON following above schema."
            payload["response_format"] = {"type": "json_object"}
        elif mode == SIMPLIFY:
            payload["messages"][-1][
                "content"
            ] += f"\n{JSONSchema().schema_prompt(schema)}"
        elif mode == TOOL_CALL:
            payload["tools"] = [
                {"type": "function", "function": {"name": "func", "parameters": schema}}
            ]
            payload["tool_choice"] = {"type": "function", "function": {"name": "func"}}
        return payload, messages

    async def llm_call(self, **kwargs):
        payload, messages = self.create_payload(**kwargs)
        logging.info(f"OPENAI PROMPT: {payload}")
        response = self.client.chat.completions.create(**payload)
        logging.info(f"OPENAI RESPONSE: {response}")
        message = response.choices[0].message
        messages.append(dict(message))
        return message, messages

    async def call(
        self,
        prompt=None,
        system_prompt=None,
        messages=None,
        schema=None,
        mode=None,
        attempts=3,
    ):
        """
        :param prompt:
        :param system_prompt:
        :param messages:
        :param schema:
        :param mode:
        :param attempts:
        :return:

        Validation checks:
            either prompt or messages must be filled
            if json_mode is true then schema cannot be None
        """
        message, messages = await self.llm_call(
            prompt=prompt,
            system_prompt=system_prompt,
            messages=messages,
            schema=schema,
            mode=mode,
        )
        if not schema:
            return messages

        i = 0
        while i < attempts:
            i += 1
            if mode == JSON_MODE:
                json_response = json.loads(message.content)
                success, error_message = Validator.validate_json(json_response, schema)
                if success:
                    return messages
                else:
                    message, messages = await self.llm_call(
                        prompt=error_message,
                        system_prompt=system_prompt,
                        messages=messages,
                        json_mode=False,
                    )
            elif mode == TOOL_CALL:
                tool_call = message.tool_calls[0]
                json_response = json.loads(tool_call.function.arguments)
                success, error_message = Validator.validate_json(json_response, schema)
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
                    message, messages = await self.llm_call(
                        messages=messages, schema=schema, json_mode=False
                    )

        messages.append({"role": "error", "content": "Failed to Adhere to JSON"})
        return messages


if __name__ == "__main__":
    import asyncio
    from fixtures import json_examples

    logging.getLogger().setLevel(logging.INFO)
    client = OpenAIClient()
    print("INPUT", json_examples[0])
    run_messages = asyncio.run(client.call(**json_examples[0], json_mode=False))
    print("OUTPUT", run_messages)
