import json
import logging
from openai_utils import OpenAIClient


class NodeState:
    def __init__(self, *args, **kwargs):
        self.system_prompt = kwargs.get("system_prompt", None)
        self.schema = kwargs.get("schema", None)
        self.response = kwargs.get("response", None)
        self.client = OpenAIClient(*args, **kwargs)

    async def process(self, prompt):
        # TODO: add self reflection for two pass response
        logging.info(f"PREV RESPONSE: {self.response}")
        if self.response:
            prompt = (
                f"Previous Response- {self.response}\nUser Query- {prompt}\n"
                f"Based on the user query you may edit the previous response, "
                f"produce a new response or give the same response back"
            )
        messages = await self.client.call(
            prompt=prompt, system_prompt=self.system_prompt, schema=self.schema
        )
        response = messages[-1]["content"]
        if self.schema:
            response = json.loads(response)
        change = response != self.response
        self.response = response
        logging.info(f"CHANGE: {change}")
        return response, change


if __name__ == "__main__":
    import asyncio
    from fixtures import json_examples

    logging.getLogger().setLevel(logging.INFO)
    response_state = NodeState(**json_examples[1])
    run_response, run_change = asyncio.run(
        response_state.process(json_examples[1]["prompt"])
    )
    print(run_response)
    print(run_change)
