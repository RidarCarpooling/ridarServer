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


def update_transaction_data(orderId, transaction_data, paymentStatus, tradeNo, credit_refund_id, paymentType=None):
    """
    Update transaction data in Firestore based on the orderId.
    """
    # Read transaction data from Firestore
    if transaction_data:
        transaction_data['paymentStatus'] = paymentStatus
        transaction_data['tradeNo'] = tradeNo
        if credit_refund_id:
            transaction_data['creditRefundId'] = credit_refund_id
        if paymentType == 'TWQR_OPAY':
            transaction_data['paymentMethod'] = 'twqr'

        # Write updated transaction data to Firestore
        write_transaction_to_firebase(orderId, transaction_data)
        
        print("Transaction data updated successfully.")
    else:
        print("Transaction data not found for orderId:", orderId)


def add_trip_to_history(user_ref, finish_time, trip_ref, moneyViaWallet):
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
            user_data = user_doc.to_dict()
            trip_history = user_data.get('trip_history', [])
            account_balance = user_data.get('account_balance', 0)
            if moneyViaWallet > 0 and account_balance > 0:
                account_balance = max(0, account_balance - moneyViaWallet)

            for trip in trip_history:
                if trip['tripRef'] == trip_ref:
                    # Set the status to 'success' if the trip already exists
                    trip['status'] = 'success'
                    user_doc_ref.update({'trip_history': trip_history, 'account_balance': account_balance})
                    print('The trips has already exists.')
                    return True
                
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
            user_doc_ref.update({'trip_history': trip_history, 'account_balance': account_balance})

            

            print('Add trip to history successfully.')
            return True
        else:
            print("User doc doesn't exist.")
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
            existing_order_index = None
            for i, order in enumerate(orders):
                if order['passengerRef'] == passenger_ref:
                    existing_order_index = i
                    break

            pendingRequest = trip_data.get('pendingRequest', 0)
            # If an existing order is found
            if existing_order_index is not None:
                existing_order = orders[existing_order_index]
                # Update passengers count based on order status
                if (existing_order['status'] == 'matching' and status == 'matching') or \
                    (existing_order['status'] == 'success' and status == 'success'):
                    existing_order['passengers'] += passengers
                    existing_order['totalPrice'] += total_price
                    existing_order['transactionId'].append(transactionId)
                elif existing_order['status'] == 'cancel':
                    existing_order['passengers'] = passengers
                    existing_order['status'] = status
                    existing_order['totalPrice'] = total_price
                    existing_order['transactionId'] = [transactionId]
                    if status == 'matching':
                        pendingRequest += 1
                elif existing_order['status'] == 'success' and status == 'matching':
                    pendingRequest += 1
                    if 'waitingOrder' not in order:
                        order['waitingOrder'] = {
                        'transactionIds': [transactionId],
                        'passengers': passengers,
                        'totalPrice': total_price
                    }
                    else:
                        order['waitingOrder']['transactionIds'].append(transactionId)
                        order['waitingOrder']['passengers'] += passengers
                        order['waitingOrder']['totalPrice'] += total_price
                print('Order has already exists')
            else:
                if status == 'matching':
                    pendingRequest += 1
                # Create a new order
                new_order = {
                    'transactionId': [transactionId],
                    'passengerRef': passenger_ref,
                    'createTime': create_time,
                    'totalPrice': total_price,
                    'passengers': passengers,
                    'status': status,
                    'alreadyComment': False,
                    'userName': userName,
                    'isCommented': False,
                    'showCommentWhileLoading': True,
                    'driverIssueProblem': False,
                    'passengerIssueProblem': False
                }
                orders.append(new_order)

            # Update other fields in the trips collection
            current_available_seats = trip_data.get('current_available_seats', 0)
            updated_seats = max(0, current_available_seats - passengers)

            passenger_user_ids = trip_data.get('passenger_userIds', [])
            passenger_user_ids.append(passenger_ref)
            passenger_user_ids = list(set(passenger_user_ids))

            included_users = trip_data.get('included_users', [])
            included_users.append(passenger_ref)
            included_users = list(set(included_users))

            passengers_num = trip_data.get('passengers_num', 0)
            updated_passengers_num = passengers_num + passengers

            # Update the trip document with the new orders list and other fields
            trip_doc_ref.update({
                'orders': orders,
                'current_available_seats': updated_seats,
                'passenger_userIds': passenger_user_ids,
                'included_users': included_users,
                'passengers_num': updated_passengers_num,
                'pendingRequest': pendingRequest
            })
            print('Add order to trip successfully!')
            return True
        else:
            return False
    except Exception as e:
        return False, f"An error occurred: {e}"


def create_notifications_doc(included_users, transaction_type, tripRef):
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
                'included_users': included_users,
                'tripRef': tripRef,
            }
        else:
            notification_data = {
                'title': '乘客發出請求',
                'title_eng': 'Passenger makes request',
                'text': '有乘客希望加入您的旅程，趕快去同意吧！',
                'text_eng': 'There is a passenger wants to join your journey, hurry up and agree!',
                'time': datetime.now(),
                'included_users': included_users,
                'tripRef': tripRef,
            }

        # Add the notification document to Firestore
        db.collection('notification').add(notification_data)

        return True
    except Exception as e:
        return False, f"An error occurred: {e}"


def update_account_balance(user_ref, moneyReturnToWallet):
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
            user_data = user_doc.to_dict()
            # Get the current trip history list
            account_balance = user_data.get('account_balance', 0)
            print('Account balance before returning', account_balance)

            account_balance += moneyReturnToWallet
            user_doc_ref.update({'account_balance': account_balance})
            print(account_balance)
            print('Refund to wallet successfully')
            return True
        else:
            return False
    except Exception as e:
        return False
    

def create_twqr_refund(userRef, orderId, amount, moneyShouldReturn, refundType, tripRef):
    """
    Create a new twqr refund document in Firestore.
    """
    refund_data = {
        'userRef': userRef,
        'orderId': orderId,
        'currentTime': datetime.now(),
        'amountAfterRefund': amount,
        'moneyShouldReturn': moneyShouldReturn,
        "refundType": refundType,
        'tripRef': tripRef
    }
    db.collection('twqr_refund').document(orderId).set(refund_data)

def create_refundFailed(userRef, orderId, tripRef, refundType):
    """
    Create a new refundFailed document in Firestore.
    """
    refundFailed = {
        'userRef': userRef,
        'transactionIds': [orderId],
        'refundTime': datetime.now(),
        'tripRef': tripRef,
        'refundType': refundType
    }
    db.collection('refundFailed').add(refundFailed)

def get_email_and_name(user_id):
    try:
        # Construct the document path using the collection name and the document ID
        user_doc_ref = db.collection('users').document(user_id)
        
        # Get the user document
        user_doc = user_doc_ref.get()
        # Check if the user document exists
        if user_doc.exists:
            user_data = user_doc.to_dict()
            email = user_data.get('email', '')
            name = user_data.get('display_name', '')
            return email, name
        else:
            return False
    except Exception as e:
        return False
