import hashlib
from urllib.parse import quote

def genCheckMacValue(orderId, transactionTime, price, buyerId, tripId):
    hashKey = '5294y06JbISpM5x9'  
    hashIV = 'v77hoKGq4kWxNNIS'  

    queryParams = {
        'MerchantID': '2000132',
        'MerchantTradeNo': orderId,
        'MerchantTradeDate': transactionTime.strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': price,
        'TradeDesc': '訂單測試',
        'ItemName': '旅程',
        'ReturnURL': 'https://ridar-server.vercel.app/return',
        # 'OrderResultURL': 'https://ridar-server.vercel.app/clientResult',
        'ChoosePayment': 'ALL',
        'ClientBackURL': f'https://ridar.com.tw/paymentResult/{orderId}?tripRef={tripId}',
        'Remark': '交易備註',
        'IgnorePayment': 'ATM#CVS#BARCODE#BNPL',
        'CustomField1': buyerId,
        'CustomField2': tripId,
        'EncryptType': '1',
    }

    sortedParams = sorted(queryParams.items(), key=lambda x: x[0])
    print(sortedParams)
    combinedParams = ''.join([f'{key}={value}&' for key, value in sortedParams])
    print(sortedParams)
    combinedParams = f'HashKey={hashKey}&{combinedParams}HashIV={hashIV}'
    print(combinedParams)

    encodedParams = quote(combinedParams, safe='')
    encodedParams = encodedParams.replace('%2d', '-').replace('%5f', '_').replace('%2e', '.').replace('%21', '!').replace('%2a', '*').replace('%28', '(').replace('%29', ')').replace('%20', '+')
    encodedParamsLower = encodedParams.lower()
    hashedParams = hashlib.sha256(encodedParamsLower.encode()).hexdigest()
    return hashedParams.upper()



