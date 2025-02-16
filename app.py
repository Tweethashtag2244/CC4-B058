from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# AIML API Key from env variables
AI_MLAPI_KEY ="59753fb258ea4fad8f31866955c2f21e"

# OpenAI Client for AIML API
client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key=AI_MLAPI_KEY,
)

# Conversation history and user preferences
conversation_history = []
user_preferences = {}

def summarize_conversation(history):
    """Summarizes long conversation history for context retention."""
    summary_prompt = "Summarize the following conversation in 2-3 sentences:\n"
    summary_prompt += "\n".join([f"{m['role']}: {m['content']}" for m in history])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.choices[0].message.content

def virtual_business_coach(prompt):
    """Handles AI-powered business coaching responses."""
    global conversation_history

    conversation_history.append({"role": "user", "content": prompt})

    # Summarize if too long
    if len(conversation_history) > 6:
        summary = summarize_conversation(conversation_history)
        conversation_history = [
            {"role": "system", "content": summary},
            conversation_history[-2],
            conversation_history[-1]
        ]

    # AI Response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history
    )
    ai_response = response.choices[0].message.content

    conversation_history.append({"role": "assistant", "content": ai_response})
    return ai_response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles user chat input."""
    user_input = request.json.get("message")
    response = virtual_business_coach(user_input)
    return jsonify({"response": response})

@app.route("/set_preferences", methods=["POST"])
def set_preferences():
    """Updates user preferences."""
    global user_preferences
    user_preferences = request.json.get("preferences", {})
    return jsonify({"status": "success", "preferences": user_preferences})

if __name__ == "__main__":
    app.run(debug=True)
