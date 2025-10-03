
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from utils import read_pdf
import gradio as gr
from tools import *

load_dotenv()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")


tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


summary = read_pdf("./summary.pdf")
name = "Rohit"

def generate_system_prompt(): 
    system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
    particularly questions related to {name}'s career, background, skills and experience. \
    Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
    You are given a summary of {name}'s background which you can use to answer questions. \
    Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
    If someone asks you anything outside do not answer politely deny that you dont know e.g like if someone asks what is databricks but this is not something i would answer right this is generic you have to answer questions specific to me   \
    If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
    If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

    system_prompt += f"\n\n## Summary:\n{summary}\n\n##"
    system_prompt += f"With this context, please chat with the user, always staying in character as {name}."
    return system_prompt

class Chatbot:
    def __init__(self, openai_client, tools):
        self.openai = openai_client
        self.tools = tools
        self.system_prompt = generate_system_prompt()

    def handle_tool_calls(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results

    def chat(self, message, history):
        history = history or []
        messages = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_calls(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content


chatbot = Chatbot(openai, tools)

# ---- Gradio UI (Blocks) ----
examples = [
    "What kinds of projects has Rohit worked on?",
    "What is Rohit's current role and expertise?",
    "Can Rohit help with an AI/LLM project?",
]

def on_send(user_message, chat_display, oa_messages):
    """Handle send: call model, update visible chat and internal OA messages state."""
    user_message = (user_message or "").strip()
    if not user_message:
        return "", chat_display, oa_messages
    assistant_reply = chatbot.chat(user_message, oa_messages)
    new_chat_display = (chat_display or []) + [(user_message, assistant_reply)]
    new_oa_messages = (oa_messages or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_reply},
    ]
    return "", new_chat_display, new_oa_messages

def on_example_click(example_text):
    return example_text

def on_contact_submit(name, email, notes, chat_display, oa_messages):
    """Submit contact info via existing tool and post a confirmation in chat."""
    confirmation = ""
    try:
        record_user_details(
            email=(email or "").strip(),
            name=(name or "not provided").strip(),
            notes=(notes or "not_provided").strip(),
        )
        confirmation = "Thanks! I’ve recorded your details and will be in touch via email."
    except Exception:
        confirmation = "Sorry, I couldn’t record your details right now. Please try again later."
    new_chat_display = (chat_display or []) + [(None, confirmation)]
    new_oa_messages = (oa_messages or []) + [{"role": "assistant", "content": confirmation}]
    return "", "", "", new_chat_display, new_oa_messages

with gr.Blocks(title=f"Chat with {name}") as demo:
    gr.Markdown(f"# Chat with {name}\nAsk about background, skills, and experience.")

    oa_messages = gr.State([])  # keeps OpenAI-style message history

    chatbot_ui = gr.Chatbot(height=420, show_copy_button=True, type="tuples")

    with gr.Row():
        user_input = gr.Textbox(label="Message", placeholder="Type your question and press Enter…", scale=8)
        send_btn = gr.Button("Send", variant="primary", scale=1)

    gr.Examples(
        examples=examples,
        inputs=[user_input],
        examples_per_page=6,
        label="Try one of these",
    )

    with gr.Accordion("Get in touch", open=False):
        with gr.Row():
            name_tb = gr.Textbox(label="Your name", placeholder="Jane Doe")
            email_tb = gr.Textbox(label="Email", placeholder="jane@example.com")
        notes_tb = gr.Textbox(label="Notes (optional)", placeholder="Tell me a bit about your needs…")
        submit_contact = gr.Button("Send contact details")

    # Wiring events
    user_input.submit(on_send, inputs=[user_input, chatbot_ui, oa_messages], outputs=[user_input, chatbot_ui, oa_messages])
    send_btn.click(on_send, inputs=[user_input, chatbot_ui, oa_messages], outputs=[user_input, chatbot_ui, oa_messages])
    submit_contact.click(
        on_contact_submit,
        inputs=[name_tb, email_tb, notes_tb, chatbot_ui, oa_messages],
        outputs=[name_tb, email_tb, notes_tb, chatbot_ui, oa_messages],
    )

demo.launch()