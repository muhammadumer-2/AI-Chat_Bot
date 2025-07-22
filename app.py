from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
import re

load_dotenv(override=True)

# --------------- Pushover Tools ------------------

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Additional info about the conversation"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

# --------------- Main Bot Class ------------------

class Me:
    def __init__(self):
        self.openai = OpenAI()
        self.name = "Ed Donner"
        self.pdf_chunks = self.load_and_chunk_pdf("file_folder/tesla.pdf", chunk_size=1000)

    def load_and_chunk_pdf(self, path, chunk_size=1000):
        reader = PdfReader(path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text.strip() + "\n"

        # Clean up and split into chunks
        full_text = re.sub(r'\s+', ' ', full_text)
        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
        return chunks

    def find_relevant_chunks(self, question, top_n=5):
        question_words = set(re.findall(r'\w+', question.lower()))
        scored_chunks = []

        for chunk in self.pdf_chunks:
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            overlap = len(question_words & chunk_words)
            scored_chunks.append((overlap, chunk))

        # Sort by word overlap and return top_n chunks
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:top_n]]

    def handle_tool_call(self, tool_calls):
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

    def system_prompt(self, context):
        return f"""You are acting as {self.name}, an expert who has read the entire Tesla-related PDF document. 
You're answering questions related to its content and context. Stay professional and accurate. 

Use only the context below to answer:

## Context:
{context}

If you don’t know the answer, use the `record_unknown_question` tool. 
If the user is interested in connecting, ask for their email and use the `record_user_details` tool.
"""

    def chat(self, message, history):
        relevant_chunks = self.find_relevant_chunks(message)
        context_text = "\n\n".join(relevant_chunks)
        messages = [{"role": "system", "content": self.system_prompt(context_text)}] + history + [{"role": "user", "content": message}]

        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

# --------------- Gradio Interface ------------------

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()
