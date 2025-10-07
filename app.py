import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    # Fake response for demo
    return jsonify({"response": f"LionMind-GPT echoes: {user_message}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
