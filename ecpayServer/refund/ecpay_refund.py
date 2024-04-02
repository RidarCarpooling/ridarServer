# Import the necessary libraries
from ecpay_payment_sdk import CreditDoAction, OrderSearch
from functions.firebase import read_transaction_from_firebase
import os

order_search_instance = OrderSearch()
orderId = ''
transactionData = read_transaction_from_firebase(orderId)
parameters = {
    'MerchantID': os.environ.get("MERCHANT_ID"),
    'MerchantTradeNo': orderId,
    'TimeStamp': 'YOUR_TIMESTAMP',  # Should be an integer
}