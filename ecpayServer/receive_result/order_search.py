import importlib.util
import time
import os

def query_order(orderId):
    # Load the module
    spec = importlib.util.spec_from_file_location(
        "ecpay_payment_sdk",
        "ecpay_payment_sdk.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Set up parameters
    order_search_params = {
        'MerchantTradeNo': orderId,
        'TimeStamp': int(time.time())
    }

    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID = os.environ.get('MERCHANT_ID'),
        HashKey = os.environ.get("HASH_KEY"),
        HashIV= os.environ.get("HASH_IV")
    )
    
    try:
        # Set the query URL
        query_url = 'https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5'  # Test environment
        # query_url = 'https://payment.ecpay.com.tw/Cashier/QueryTradeInfo/V5'  # 正式環境
        # Query the order
        query_result = ecpay_payment_sdk.order_search(
            action_url=query_url,
            client_parameters=order_search_params
        )
        return query_result

    except Exception as error:
        print('An exception happened: ' + str(error))
        return None