from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import chatbot,append_to_chat
from dotenv import load_dotenv
from firebaseconfig import auth
from firebaseconfig import db  


app = FastAPI(
    title="My chatbot with gpt-4o-mini",
    summary="En este chat puedes crear/emininar/cotinuar un chat y cambiar el titulo de un chat",
    version="0.0.1"
)
load_dotenv()

class UserCreate(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatUpdate(BaseModel):
    new_title: str 

class ChatContinue(BaseModel):
    prompt: str

# Endpoint para el registro (signup)
@app.post("/signup", tags=["Firebase auth"])
async def signup(user: UserCreate):
    try:
        new_user = auth.create_user(
            email=user.email,
            password=user.password
        )
        return {"uid": new_user.uid, "email": new_user.email}
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="El correo ya existe")

# Endpoint para el login
@app.post("/login", tags=["Firebase auth"])
async def login(login_request: LoginRequest):
    email = login_request.email
    password = login_request.password
    try:
        user = auth.get_user_by_email(email)
        # Generar un token personalizado
        custom_token = auth.create_custom_token(user.uid)
        return {"token": custom_token}
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
#endpoint para el chatbot 
@app.get("/chatbot/", tags=["My chatbot"])
async def Create_NewChat(prompt: str):
    response = chatbot(prompt)
    return {"response": response}

#ver el historia de chats
@app.get("/chats", tags=["My chatbot"])
async def get_AllChats():
        chats_ref = db.collection("Chatbot").stream()
        chats = [{"id": chat.id, 
                  **chat.to_dict()} 
                  for chat in chats_ref]
        return {"chats": chats} 


#modificar titulo by id
@app.put("/update-chat-title/{chat_id}", tags=["My chatbot"])
async def Update_ChatTitle(chat_id:str, chat_update:ChatUpdate):
    chat_ref = db.collection("Chatbot").document(chat_id)
    chat = chat_ref.get()
    if not chat.exists:
        raise HTTPException(status_code=404, detail="Chat no existe!")
    chat_ref.update({"title": chat_update.new_title})
    return{"message": "titulo Actualizado!"}

#eliminar chat
@app.delete("/delete-chat/{chat_id}", tags=["My chatbot"])
async def delete_chat(chat_id: str):
    chat_ref = db.collection("Chatbot").document(chat_id)
    chat = chat_ref.get()
    if not chat.exists:
        raise HTTPException(status_code=404, detail="Chat no existe!")
    chat_ref.delete()
    return {"message":"chat eliminado con exito!", "chat_id":chat_id}


#continuar un chat
@app.post("/chat/{chat_id}/continue", tags=["continuar chatbot"])
async def continue_chat(chat_id: str, chat_input: ChatContinue):
    chat_ref = db.collection("Chatbot").document(chat_id)
    chat = chat_ref.get()

    if not chat.exists:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    bot_response = chatbot(chat_input.prompt)

    # Agregar el nuevo mensaje a la conversación
    updated_chat = append_to_chat(chat_id, chat_input.prompt, bot_response)

    if updated_chat is None:
        raise HTTPException(status_code=500, detail="Error al actualizar el chat")

    return {"chat": updated_chat}