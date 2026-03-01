#-*- coding: utf-8

from graph.graph import init_app
from utils.helper import save_chat_history, get_thread_id
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import warnings
from langchain_core._api.beta_decorator import LangChainBetaWarning
from dotenv import load_dotenv, find_dotenv
import json

# Ignore warnings of specific category
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

def chat(user_message, app, config):
    formatted_user_message = HumanMessage(content=user_message)
    for event in app.stream({"messages": formatted_user_message}, config=config,):
        for value in event.values():
            message = value["messages"][-1]
            content = message.content

            if isinstance(message, AIMessage):
                if message.tool_calls:
                    if content:
                        print(content)
                    print("--")
                    for tool_call in message.tool_calls:
                        print(f"Starting tool: {tool_call['name']} with inputs: {tool_call['args']}")
                else:
                    # the message to the user
                    print(content)

            if isinstance(message, ToolMessage):
                tool_messages = []
                for msg in reversed(value["messages"]):
                    if isinstance(msg, ToolMessage):
                        tool_messages.append(msg)
                    else:
                        break

                for tool_message in reversed(tool_messages):
                    print("\nTool output:")
                    content = tool_message.content
                    try:
                        decoded_content = json.loads(content)
                        print(decoded_content)
                    except json.JSONDecodeError:
                        print(content)
                    print("--")


if __name__ == "__main__":
    _ = load_dotenv(find_dotenv())
    app = init_app(model_name="gemini-1.5-flash-latest", is_async=False)
    thread_id = get_thread_id()
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_message = input("\n用户:")
        if user_message.strip() == "":
            save_chat_history(app, thread_id)
            print("Chat history saved.\n")
            break
        print("AI:", end="")
        chat(user_message, app, config)

