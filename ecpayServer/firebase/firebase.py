from firebase_admin import firestore, initialize_app
import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ridar-e1rlvk-firebase-adminsdk-31um4-04d2182145.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
initialize_app()

def create_transaction_document(transaction_data, orderId):
    """
    Create a new transaction document in Firestore with a new transaction ID.
    """
    db = firestore.client()
    db.collection('transactions').document(orderId).set(transaction_data)
    
def read_from_firebase(transaction_id):
    """
    Retrieve a transaction document from Firestore based on the provided transaction ID.
    """
    db = firestore.client()
    transaction_doc = db.collection('transactions').document(transaction_id).get()
    return transaction_doc.to_dict()

def write_to_firebase(transaction_id, transaction_data):
    """
    Write a transaction document to Firestore.
    """
    db = firestore.client()
    db.collection('transactions').document(transaction_id).set(transaction_data)
    return transaction_id

    