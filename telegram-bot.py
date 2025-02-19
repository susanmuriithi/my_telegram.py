from flask import Flask, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask("telegram_bot")

# Get token and bot name from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')  # usually "bot" is used, so URL becomes "https://api.telegram.org/bot<token>"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
print(f"Telegram API URL: {TELEGRAM_API_URL}")

def chatbot_response(message):
    message = message.lower()
    
    # Predefined responses
    responses = {
        "hello": "Hi there! How can I help you?",
        "hi": "Hello! What can I do for you today?",
        "how are you": "I'm just a bot, but I'm doing great! What about you?",
        "bye": "Goodbye! Have a great day!",
        "help": "I can help you with basic conversations. Try saying hello!"
    }
    
    # Check if any keyword is in the message
    for key in responses:
        if key in message:
            return responses[key]
            
    return "I'm not sure how to respond to that. Try saying 'help' for more information."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()

        # Check if the update is an inline query
        if 'inline_query' in update:
            inline_query = update['inline_query']
            query_id = inline_query['id']
            query_text = inline_query['query']
            
            # Define inline query results based on predefined commands.
            # You can customize these as needed.
            results = []
            
            # Example inline result for "help"
            if query_text.strip().lower() == "help" or query_text.strip() == "":
                results.append({
                    'type': 'article',
                    'id': '1',
                    'title': 'Help',
                    'description': 'List available commands.',
                    'input_message_content': {
                        'message_text': "Available commands:\n- hello\n- hi\n- how are you\n- bye\n- help"
                    }
                })
            # Example inline result for "hello"
            if "hello" in query_text.lower():
                results.append({
                    'type': 'article',
                    'id': '2',
                    'title': 'Greet',
                    'description': 'Say Hello',
                    'input_message_content': {
                        'message_text': "Hi there! How can I help you?"
                    }
                })
            # You can add more inline query results for different commands here.
            
            data = {
                'inline_query_id': query_id,
                'results': json.dumps(results)  # Telegram expects a JSON-serialized list
            }
            
            # Respond to the inline query
            requests.post(f"{TELEGRAM_API_URL}/answerInlineQuery", json=data, verify=False)
            return 'OK'
        
        # Process regular messages
        if 'message' not in update:
            return jsonify({'error': 'No message found'}), 400
            
        chat_id = update['message']['chat']['id']
        message_text = update['message']['text']
        
        response_text = chatbot_response(message_text)
        
        data = {
            'chat_id': chat_id,
            'text': response_text
        }
        
        # Send the response message back to Telegram
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=data, verify=False)
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
    
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json=data, verify=False)
    return f"Webhook setup response: {response.text}"

@app.route('/')
def test():
    return "Bot is running!"

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set in environment variables")
    app.run(debug=True)
