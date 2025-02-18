from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask("telegram_bot")

# Get token from environment variable
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def chatbot_response(message):
    message = message.lower()
    
    # Enhanced response dictionary
    responses = {
        "hello": "Hi there! How can I help you?",
        "hi": "Hello! What can I do for you today?",
        "how are you": "I'm just a bot, but I'm doing great! What about you?",
        "bye": "Goodbye! Have a great day!",
        "help": "I can help you with basic conversations. Try saying hello!"
    }
    
    # Check for matching keywords
    for key in responses:
        if key in message:
            return responses[key]
            
    return "I'm not sure how to respond to that. Try saying 'help' for more information."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        
        # Enhanced error handling for message structure
        if 'message' not in update:
            return jsonify({'error': 'No message found'}), 400
            
        chat_id = update['message']['chat']['id']
        message_text = update['message']['text']
        
        response = chatbot_response(message_text)
        
        data = {
            'chat_id': chat_id,
            'text': response
        }
        
        # Send response to Telegram
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json=data,
            verify=False
        )
        
        return 'OK'
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/setup_webhook')
def setup_webhook():
    # Get webhook URL from environment variable
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if not webhook_url:
        return "Webhook URL not configured", 400
        
    data = {'url': webhook_url}
    
    response = requests.post(
        f"{TELEGRAM_API_URL}/setWebhook",
        json=data,
        verify=False
    )
    return f"Webhook setup response: {response.text}"

@app.route('/')
def test():
    return "Bot is running!"

if __name__ == '__main__':
    # Make sure required environment variables are set
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set in environment variables")
    app.run(debug=True)