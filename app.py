from flask import Flask, request, jsonify, render_template, session
import os
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    system_instruction = (
        "You are MeowAI, a professional virtual business coach. "
        "You provide actionable business advice, help with strategic planning, "
        "market analysis, startup mentoring, and decision-making support. "
        "Only answer questions from a business coaching perspective. "
        "Keep responses relevant to business, finance, startups, productivity, or entrepreneurship. "
        "Be concise and actionable."
    )

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_instruction

    )

except ValueError as e:
    print(f"Error initializing Gemini: {e}")
    model = None
except Exception as e:
    print(f"An unexpected error occurred during Gemini initialization: {e}")
    model = None

user_chat_sessions = {}

@app.route("/")
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        print(f"New session created: {session['session_id']}")
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not model:
         return jsonify({"error": "Chat model not initialized. Please check server configuration."}), 500

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        print(f"Session ID missing, created new one: {session['session_id']}")

    session_id = session['session_id']

    try:
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        if session_id not in user_chat_sessions:
            print(f"Starting new chat session for {session_id}")
            user_chat_sessions[session_id] = model.start_chat(history=[])

        chat_session = user_chat_sessions[session_id]
        response = chat_session.send_message(user_input)
        return jsonify({"response": f"{response.text}"})
    except KeyError:
         return jsonify({"error": "Invalid request format. 'message' key missing."}), 400
    except Exception as e:
        print(f"Error during chat processing for session {session_id}: {e}")
        return jsonify({"error": f"An internal error occurred: {e}"}), 500
@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    session_id = session.get('session_id')
    if session_id and session_id in user_chat_sessions:
        del user_chat_sessions[session_id]
        print(f"Cleared chat history for session {session_id}")
        return jsonify({"status": "Chat history cleared"}), 200
    elif session_id:
         return jsonify({"status": "No active chat history to clear"}), 200
    else:
        return jsonify({"error": "No session found"}), 400


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
