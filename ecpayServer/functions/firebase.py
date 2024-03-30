from firebase_admin import firestore

# def initialize_firebase():
#     """
#     Initialize Firebase Admin SDK using environment variables.
#     """
#     firebase_credentials = {
#         "type": "service_account",
#         "project_id": os.environ.get("PROJECT_ID"),
#         "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
#         "private_key": os.environ.get("PRIVATE_KEY").replace('\\n', '\n'),  # Replace escaped newlines
#         "client_email": os.environ.get("CLIENT_EMAIL"),
#         "client_id": os.environ.get("CLIENT_ID"),
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/tokenn",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "client_x509_cert_url": os.environ.get("CLIENT_CERT_URL")
#     }

#     initialize_app(credential=firebase_credentials)

# initialize_app()

def create_transaction_document(transaction_data, orderId):
    """
    Create a new transaction document in Firestore with a new transaction ID.
    """
    db = firestore.client()
    db.collection('transactions').document(orderId).set(transaction_data)
    
def read_transaction_from_firebase(transaction_id):
    """
    Retrieve a transaction document from Firestore based on the provided transaction ID.
    """
    db = firestore.client()
    transaction_doc = db.collection('transactions').document(transaction_id).get()
    return transaction_doc.to_dict()

def write_transaction_to_firebase(transaction_id, transaction_data):
    """
    Write a transaction document to Firestore.
    """
    db = firestore.client()
    db.collection('transactions').document(transaction_id).set(transaction_data)
    return transaction_id
