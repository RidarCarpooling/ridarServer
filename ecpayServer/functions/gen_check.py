# import hashlib
# from urllib.parse import quote_plus

# def genCheckMacValue(orderId, transactionTime, price, buyerId, tripId):
#     hashKey = 'pwFHCqoQZGmho4w6'  
#     hashIV = 'EkRm7iFT261dpevs'  

#     print(orderId, transactionTime, price, buyerId, tripId)
#     queryParams = {
#         'MerchantID': '3002607',
#         'MerchantTradeNo': orderId,
#         'MerchantTradeDate': transactionTime.strftime("%Y/%m/%d %H:%M:%S"),
#         'PaymentType': 'aio',
#         'TotalAmount': 350,
#         'TradeDesc': '促銷方案',
#         'ItemName': '旅程',
#         'ReturnURL': 'https://ridar-server.vercel.app/return',
#         # 'OrderResultURL': 'https://ridar-server.vercel.app/clientResult',
#         'ChoosePayment': 'ALL',
#         # 'ClientBackURL': f'https://ridar.com.tw/paymentResult/{orderId}?tripRef={tripId}',
#         # 'Remark': '交易備註',
#         # 'IgnorePayment': 'ATM#CVS#BARCODE#BNPL',
#         # 'CustomField1': buyerId,
#         # 'CustomField2': tripId,
#         'EncryptType': 1,
#     }

#     sortedParams = sorted(queryParams.items(), key=lambda x: x[0])
#     print(sortedParams)
#     combinedParams = ''.join([f'{key}={value}&' for key, value in sortedParams])
#     combinedParams = f'HashKey={hashKey}&{combinedParams}HashIV={hashIV}'
#     safe_characters = '-_.!*()'
#     print(combinedParams)
#     encoding_str = quote_plus(str(combinedParams), safe=safe_characters).lower()
#     print(encoding_str)
#     check_mac_value = hashlib.sha256(
#         encoding_str.encode('utf-8')).hexdigest().upper()

#     return check_mac_value



# # import datetime
# # orderId = 'ridar202403301651175'
# # transactionTime = "2024/03/30 16:51:17"
# # price = 350
# # buyerId = 'xOSutkNOS3TmnW4pMPyXouA2Ew43'
# # tripId = ''
# # checkMacValue = genCheckMacValue(orderId, transactionTime, price, buyerId, tripId)
# # print(checkMacValue)

import importlib.util
import hashlib
from urllib.parse import quote_plus
import collections
import copy

# Create module specification
def gen_check_mac_value(orderId, transactionTime):
    spec = importlib.util.spec_from_file_location(
        "ecpay_payment_sdk",
        "ecpay_payment_sdk.py"
    )

    # Create module from specification
    module = importlib.util.module_from_spec(spec)

    # Load the module
    spec.loader.exec_module(module)

    # Create an instance of the ECPayPaymentSdk class
    ecpay_sdk = module.ECPayPaymentSdk(MerchantID='3002607', HashKey='pwFHCqoQZGmho4w6', HashIV='EkRm7iFT261dpevs')

    # Prepare your parameters
    params = {
        'MerchantTradeNo':  orderId,
        # datetime.now().strftime("NO%Y%m%d%H%M%S"),
        # 'StoreID': '',
        'MerchantTradeDate': transactionTime.strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': 350,
        'TradeDesc': '訂單測試',
        'ItemName': '旅程',
        'ReturnURL': 'https://ridar-server.vercel.app/return',
        'ChoosePayment': 'ALL',
        # 'ClientBackURL': f'https://ridar.com.tw/paymentResult/{orderId}?tripRef={tripReference}',
        # 'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
        # 'Remark': '交易備註',
        # 'ChooseSubPayment': '',
        # 'OrderResultURL': 'https://ridar-server.vercel.app/clientResult',
        # 'NeedExtraPaidInfo': 'Y',
        # 'DeviceSource': '',
        # 'IgnorePayment': 'ATM#CVS#BARCODE#BNPL',
        # 'PlatformID': '',
        # 'InvoiceMark': 'N',
        # 'CustomField1': buyerId,
        # 'CustomField2': tripReference,
        # 'CustomField3': '',
        # 'CustomField4': '',
        'EncryptType': 1,
    }

    # Call the generate_check_value method
    check_mac_value = ecpay_sdk.generate_check_value(params)

    # Now you have the check MAC value
    print(check_mac_value)
    return check_mac_value
