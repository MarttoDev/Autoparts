import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("autoparts-sdk.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Cliente de Firestore
db = firestore.client()
