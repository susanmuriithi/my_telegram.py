from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Optional, Dict, Any, List
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Telegram Bot")

# Get token and bot name from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_NAME = os.getenv('BOT_NAME', 'bot')  # Default to 'bot' if not specified
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
print(TELEGRAM_API_URL)

# Pydantic models for request validation
class InlineQueryResult(BaseModel):
    type: str
    id: str
    title: str
    description: str
    input_message_content: Dict[str, str]

class InlineQuery(BaseModel):
    id: str
    query: str

class Message(BaseModel):
    chat: Dict[str, Any]
    text: str

class Update(BaseModel):
    inline_query: Optional[InlineQuery] = None
    message: Optional[Message] = None

def chatbot_response(message: str) -> str:
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

@app.post("/webhook")
async def webhook(update: Update):
    try:
        # Handle inline queries
        if update.inline_query:
            query_id = update.inline_query.id
            query_text = update.inline_query.query
            
            results: List[Dict[str, Any]] = []
            
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
            
            data = {
                'inline_query_id': query_id,
                'results': json.dumps(results)
            }
            
            requests.post(f"{TELEGRAM_API_URL}/answerInlineQuery", json=data)
            return {"status": "ok"}
        
        # Handle regular messages
        if update.message:
            chat_id = update.message.chat['id']
            message_text = update.message.text
            
            response_text = chatbot_response(message_text)
            
            data = {
                'chat_id': chat_id,
                'text': response_text
            }
            
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=data)
            return {"status": "ok"}
            
        raise HTTPException(status_code=400, detail="Invalid update received")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/setup_webhook")
async def setup_webhook():
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if not webhook_url:
        raise HTTPException(status_code=400, detail="Webhook URL not configured")
        
    data = {'url': webhook_url}
    
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json=data)
    return {"message": f"Webhook setup response: {response.text}"}


@app.get("/get_webhook_info")
async def get_webhook_info():
    response = requests.post(f"{TELEGRAM_API_URL}/getWebhookInfo")
    return response.json()

@app.get("/")
async def root():
    return {"status": "Bot is running!"}

if __name__ == "__main__":
    import uvicorn
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not set in environment variables")
    uvicorn.run(app, host="0.0.0.0", port=8000)