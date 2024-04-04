# -*- coding: utf-8 -*-

import importlib.util
spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    "ecpay_payment_sdk.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
import os

def search_single_transaction(CreditRefundId, CreditAmount):
    """
    Search for a single transaction using the ECPayPaymentSdk module.
    """
    try:
        # 信用卡授權單號、金額、商家檢查碼
        search_single_transaction_params = {
            'CreditRefundId': CreditRefundId,
            'CreditAmount': CreditAmount,
            'CreditCheckCode': os.environ.get("CREDIT_CHECK_CODE")
        }

        # 建立實體
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID=os.environ.get("MERCHANT_ID"),
            HashKey=os.environ.get("HASH_KEY"),
            HashIV=os.environ.get("HASH_IV")
        )

        # 介接路徑
        # query_url = '因無法提供實際授權，故無法使用此API' # 測試環境
        query_url = 'https://payment.ecPay.com.tw/CreditDetail/QueryTrade/V2'  # 正式環境

        # 查詢訂單
        query_result = ecpay_payment_sdk.search_single_transaction(
            client_parameters=search_single_transaction_params)
        return query_result

    except Exception as error:
        print('An exception happened: ' + str(error))
        return None
