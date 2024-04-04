# -*- coding: utf-8 -*-

import importlib.util
spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    "ecpay_payment_sdk.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
import pprint
import os


def perform_credit_do_action(orderId, tradeNo, totalAmount, action):
    credit_do_action_params = {
        'MerchantTradeNo': orderId,
        'TradeNo': tradeNo,
        'Action': action,
        'TotalAmount': totalAmount,
    }

    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID=os.environ.get("MERCHANT_ID"),
        HashKey=os.environ.get("HASH_KEY"),
        HashIV=os.environ.get("HASH_IV")
    )

    try:
        query_url = 'https://payment.ecpay.com.tw/CreditDetail/DoAction'
        query_result = ecpay_payment_sdk.credit_do_action(
            client_parameters=credit_do_action_params)
        pprint.pprint(query_result)
    except Exception as error:
        print('An exception happened: ' + str(error))
