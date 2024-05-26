import asyncio
import json
import logging
import streamlit as st

from state import ResponseState
from fixtures import schema_examples

TITLE = "JSON-PLANNER"
USER = "user"
ASSISTANT = "assistant"


async def run_function(payload):
    prompt = payload["messages"][-1]["content"]
    run_response, run_change = await st.session_state["chart_state"].process(prompt)
    return run_response


def app():
    st.title(TITLE)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state["chart_state"] = ResponseState(schema=schema_examples["chart_type_schema"])

    for i, message in enumerate(
        st.session_state.messages
    ):  # display all the previous message
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("you")
    if user_input:
        st.chat_message(USER).write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        payload = {"messages": st.session_state.messages}

        with st.spinner("Running"):
            logging.info(f"{'-'*150}")
            logging.info(f"REQ: {payload}")
            response = asyncio.run(run_function(payload))
            logging.info(f"RESP: {response}")

        bot_answer = response
        try:
            bot_answer = json.loads(response)
        except Exception:
            pass
        st.chat_message(ASSISTANT).write(bot_answer)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    app()
