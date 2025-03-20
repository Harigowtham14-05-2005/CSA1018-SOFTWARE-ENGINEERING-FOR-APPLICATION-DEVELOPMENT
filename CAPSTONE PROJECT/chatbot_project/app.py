

# Flask App Setup
app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Replace with a secure key
CORS(app)

# Google Gemini API Setup
GEMINI_API_KEY = "AIzaSyAfGwjlWaFpdO4JB1L-GUmUo_hp3gRqpGE"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Jira API Credentials (Replace with your details)
JIRA_DOMAIN = "h4525731.atlassian.net"  # Example: company.atlassian.net
JIRA_EMAIL = "h4525731@gmail.com"  # Your Jira login email
JIRA_API_TOKEN = "ATATT3xFfGF0X8j2zCOZDs07uVQwLe_-QUBrGzdtxbnn1ghx2VECudJs8hAyC2nWHNBYU93k1c8mLP2iHsNwx2lx2kcYFBNk8xK84erfdpJjq3yJqR8_jsnTzWrxyoEqLPiT-lXlXY8mJkxX1vmLBa_yGzl5j1fufbhVYoAFrbKHD1WB-rJmKL4=012C65B7"  # Generate from https://id.atlassian.com/manage/api-tokens
JIRA_PROJECT_KEY = "CHAT_BOT"  # Your Jira project key

# Encode credentials for authentication
auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()
JIRA_URL = f"https://{JIRA_DOMAIN}/rest/api/3/issue"

# Function to generate chatbot response
def chatbot_response(user_input):
    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id  # Assign session ID if not already set

    history = session.get("history", [])  # Retrieve past conversation
    history.append(f"User: {user_input}")

    prompt = "You're an AI chatbot helping with software requirement gathering.\n"
    prompt += "\n".join(history[-5:])  # Use last 5 interactions for context

    try:
        response = model.generate_content(prompt)
        bot_response = response.text.strip()
        history.append(f"Bot: {bot_response}")
        session["history"] = history  # Save conversation history

        return bot_response
    except Exception as e:
        return f"Error: {str(e)}"

# Function to export requirement to Jira
def export_to_jira(requirement):
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": "New Requirement",
            "description": requirement,
            "issuetype": {"name": "Task"}
        }
    }

    response = requests.post(JIRA_URL, json=data, headers=headers)

    if response.status_code == 201:
        return {"status": "Success", "message": "Requirement exported to Jira"}
    else:
        return {"status": "Error", "details": response.json()}

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = chatbot_response(user_input)
    return jsonify({"response": response})

@app.route("/export", methods=["POST"])
def export():
    requirement = request.json.get("requirement")
    export_result = export_to_jira(requirement)
    return jsonify(export_result)

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import google.generativeai as genai
import requests
import base64
import uuid