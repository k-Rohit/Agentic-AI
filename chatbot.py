
from openai import OpenAI
import os
import json
from utils import read_pdf
import streamlit as st
from tools import *

# Initialize OpenAI client using Streamlit secrets
openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

PUSHOVER_USER = st.secrets["PUSHOVER_USER"]
PUSHOVER_TOKEN = st.secrets["PUSHOVER_TOKEN"]


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

# ---- Streamlit UI ----
def main():
    st.set_page_config(page_title=f"Chat with {name}", page_icon="🤖", layout="wide")
    
    st.markdown(f"# 🤖 Chat with {name}")
    st.markdown("Ask about background, skills, and experience.")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "oa_messages" not in st.session_state:
        st.session_state.oa_messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Example questions
    examples = [
        "What kinds of projects has Rohit worked on?",
        "What is Rohit's current role and expertise?",
        "Can Rohit help with an AI/LLM project?",
    ]
    
    st.markdown("### Try one of these:")
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.user_input = example
    
    # Chat input
    if prompt := st.chat_input("Type your question and press Enter…"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.oa_messages.append({"role": "user", "content": prompt})
        

        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.chat(prompt, st.session_state.oa_messages)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.oa_messages.append({"role": "assistant", "content": response})
    
    if hasattr(st.session_state, 'user_input'):
        prompt = st.session_state.user_input
        delattr(st.session_state, 'user_input')
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.oa_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.chat(prompt, st.session_state.oa_messages)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.oa_messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Contact form
    with st.expander("Get in touch", expanded=False):
        with st.form("contact_form"):
            user_name = st.text_input("Your name", placeholder="Jane Doe")
            email = st.text_input("Email", placeholder="jane@example.com")
            notes = st.text_area("Notes (optional)", placeholder="Tell me a bit about your needs…")
            
            if st.form_submit_button("Send contact details"):
                try:
                    record_user_details(
                        email=email.strip() if email else "",
                        name=user_name.strip() if user_name else "not provided",
                        notes=notes.strip() if notes else "not_provided",
                    )
                    confirmation = "Thanks! I've recorded your details and will be in touch via email."
                    st.success(confirmation)
                except Exception:
                    confirmation = "Sorry, I couldn't record your details right now. Please try again later."
                    st.error(confirmation)
                
                # Add confirmation to chat
                st.session_state.messages.append({"role": "assistant", "content": confirmation})
                st.session_state.oa_messages.append({"role": "assistant", "content": confirmation})
                st.rerun()

if __name__ == "__main__":
    main()
