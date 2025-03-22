import os
from openai import OpenAI
from dotenv import load_dotenv
from firebaseconfig import db
import uuid
load_dotenv()


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")  # https://api.openai.com/v1 -> Custom server
)


def firestiresave(user_prompt: str, bot_response: str):
    chat_title = user_prompt[:50]
    chat_id = str(uuid.uuid4())  
    chat_ref = db.collection("Chatbot").document(chat_id).set({
        "id": chat_id,
        "title": chat_title,
        "user_prompt": user_prompt,
        "bot_response": bot_response
    })
    return chat_id  


#chatbot
def chatbot(prompt: str) -> str:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that can answer questions and help with tasks."},
                {"role": "user", "content": prompt}
            ],
            user="yoshio.soto@softtek.com"
        )
        bot_response = response.choices[0].message.content
        firestiresave(prompt, bot_response)
        return bot_response


