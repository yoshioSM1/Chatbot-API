import firebase_admin
from firebase_admin import credentials, auth, firestore

# Inicializar Firebase
def initialize_firebase():
    cred = credentials.Certificate("academia-10796-firebase-adminsdk-fbsvc-15274f6725.json")
    firebase_app = firebase_admin.initialize_app(cred)
    return firebase_app

# Exportar funciones de autenticación y Firestore
def get_auth():
    return auth

def get_firestore():
    return firestore.client()

# Inicializar Firebase al importar el módulo
firebase_app = initialize_firebase()
auth = get_auth()
db = get_firestore()  # Inicializar Firestore