from firebase_admin import firestore, initialize_app, credentials
import os
from datetime import datetime

def initialize_firebase():
    """
    Initialize Firebase Admin SDK using a service account key file.
    """
    # Check if the service account key file path is set in the environment variable
    service_account_key_path = 'ridar-e1rlvk-firebase-adminsdk-31um4-04d2182145.json'
    
    if not service_account_key_path:
        print("Error: Service account key file path is not set in the environment variable.")
        return
    
    # Initialize Firebase with the service account key file
    cred = credentials.Certificate(service_account_key_path)
    initialize_app(cred)

# Call the initialize_firebase function to initialize Firebase
# initialize_firebase()

db = firestore.client()

def create_transaction_document(transaction_data, orderId):
    """
    Create a new transaction document in Firestore with a new transaction ID.
    """

    db.collection('transactions').document(orderId).set(transaction_data)
    
def read_transaction_from_firebase(transaction_id):
    """
    Retrieve a transaction document from Firestore based on the provided transaction ID.
    """

    transaction_doc = db.collection('transactions').document(transaction_id).get()
    return transaction_doc.to_dict()

def write_transaction_to_firebase(transaction_id, transaction_data):
    """
    Write a transaction document to Firestore.
    """

    db.collection('transactions').document(transaction_id).set(transaction_data)
    return transaction_id


def update_transaction_data(orderId, transaction_data, paymentStatus, tradeNo, credit_refund_id):
    """
    Update transaction data in Firestore based on the orderId.
    """
    # Read transaction data from Firestore
    
    if transaction_data:
        transaction_data['paymentStatus'] = paymentStatus
        transaction_data['tradeNo'] = tradeNo
        if credit_refund_id:
            transaction_data['creditRefundId'] = credit_refund_id
        
        # Write updated transaction data to Firestore
        write_transaction_to_firebase(orderId, transaction_data)
        
        print("Transaction data updated successfully.")
    else:
        print("Transaction data not found for orderId:", orderId)


def add_trip_to_history(user_ref, finish_time, trip_ref):
    """
    Add a trip to the trip_history list of a user document in Firestore.
    """
    # Get the Firestore client
    
    try:

        # Get the user document
        user_doc_ref = db.document(user_ref.path)
        user_doc = user_doc_ref.get()

        # Check if the user document exists
        if user_doc.exists:
            # Get the current trip history list
            trip_history = user_doc.to_dict().get('trip_history', [])

            # Calculate the reverse index
            reverse_index = -(len(trip_history) + 1)

            # Create the new trip data
            new_trip = {
                'finishTime': finish_time,
                'isDriver': False,
                'reverse_index': reverse_index,
                'status': 'success',
                'tripRef': trip_ref
            }

            # Append the new trip to the trip history list
            trip_history.append(new_trip)

            # Update the user document with the new trip history list
            user_doc_ref.update({'trip_history': trip_history})

            print('Add trip to history successfully.')
            return True
        else:
            return False
    except Exception as e:
        return False, f"An error occurred: {e}"
    

def add_order_to_trip(trip_ref, passenger_ref, create_time, total_price, passengers, userName, transaction_type, transactionId):
    """
    Add an order to the orders list of a trip document in Firestore.
    Update other fields in the trips collection.
    """
    # Get the Firestore client

    try:
        # Get the trip document
        trip_doc_ref = db.document(trip_ref.path)
        trip_doc = trip_doc_ref.get()

        # Check if the trip document exists
        if trip_doc.exists:
            # Get the current trip data
            trip_data = trip_doc.to_dict()

            # Get the current orders list
            orders = trip_data.get('orders', [])

            # Determine the status based on transaction type
            if transaction_type == 'success':
                status = 'success'
            else:
                status = 'matching'

            # Create the new order data
            new_order = {
                'transactionId': transactionId,
                'passengerRef': passenger_ref,
                'createTime': create_time,
                'totalPrice': total_price,
                'passengers': passengers,
                'status': status,
                'alreadyComment': False,
                'userName': userName,
                'isCommented': False,
                'showCommentWhileLoading': True
            }

            # Append the new order to the orders list
            orders.append(new_order)

            # Update other fields in the trips collection
            current_available_seats = trip_data.get('current_available_seats', 0)
            updated_seats = max(0, current_available_seats - passengers)

            passenger_user_ids = trip_data.get('passenger_userIds', [])
            passenger_user_ids.append(passenger_ref)

            included_users = trip_data.get('included_users', [])
            included_users.append(passenger_ref)

            passengers_num = trip_data.get('passengers_num', 0)
            updated_passengers_num = passengers_num + passengers

            # Update the trip document with the new orders list and other fields
            trip_doc_ref.update({
                'orders': orders,
                'current_available_seats': updated_seats,
                'passenger_userIds': passenger_user_ids,
                'included_users': included_users,
                'passengers_num': updated_passengers_num
            })
            print('Add order to trip successfully!')
            return True
        else:
            return False
    except Exception as e:
        return False, f"An error occurred: {e}"


def create_notifications_doc(included_users, transaction_type):
    """
    Create a notifications document in Firestore.
    """
    # Get the Firestore client

    try:
        # Prepare notification data
        if transaction_type == 'success':
            notification_data = {
                'title': '訂單通知',
                'title_eng': 'Order notification',
                'text': '用戶成功加入旅程，歡迎私訊對方確認旅程細節。',
                'text_eng': 'The user has successfully joined the trip and is welcome to send a message to the other party to confirm the trip details.',
                'time': datetime.now(),
                'included_users': included_users
            }
        else:
            notification_data = {
                'title': '乘客發出請求',
                'title_eng': 'Passenger makes request',
                'text': '有乘客希望加入您的旅程，趕快去同意吧！',
                'text_eng': 'There is a passenger wants to join your journey, hurry up and agree!',
                'time': datetime.now(),
                'included_users': included_users
            }

        # Add the notification document to Firestore
        db.collection('notifications').add(notification_data)

        return True
    except Exception as e:
        return False, f"An error occurred: {e}"
