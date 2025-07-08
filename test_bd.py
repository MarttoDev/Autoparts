from autoapp.firebase_config import db

def test_firebase():
    doc_ref = db.collection('test').document('ping')
    doc_ref.set({'mensaje': 'test desde Django'})
    print("Documento de prueba creado")

if __name__ == "__main__":
    test_firebase()
