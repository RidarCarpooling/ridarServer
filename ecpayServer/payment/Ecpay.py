# -*- coding: utf-8 -*-

import importlib.util
spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    "ecpay_payment_sdk.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
from datetime import datetime
import os


def main(totalAmount, orderId, transactionTime, buyerId, tripReference, lang):

    order_params = {
        'MerchantTradeNo':  orderId,
        # datetime.now().strftime("NO%Y%m%d%H%M%S"),
        # 'StoreID': '',
        'MerchantTradeDate': transactionTime.strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': totalAmount,
        'TradeDesc': '訂單測試',
        'ItemName': '旅程',
        'ReturnURL': 'https://server.ridar.com.tw/return',
        'ChoosePayment': 'ALL',
        'ClientBackURL': f'https://ridar.com.tw/paymentResult/{orderId}?tripRef={tripReference}',
        # 'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
        # 'Remark': '交易備註',
        # 'ChooseSubPayment': '',
        # 'OrderResultURL': 'https://ridar-server.vercel.app/clientResult',
        'NeedExtraPaidInfo': 'Y',
        # 'DeviceSource': '',
        'IgnorePayment': 'WebATM#ATM#CVS#BARCODE#BNPL',
        # 'PlatformID': '',
        # 'InvoiceMark': 'N',
        'CustomField1': buyerId,
        'CustomField2': tripReference,
        # 'CustomField3': '',
        # 'CustomField4': '',
        'EncryptType': 1,
    }
    if lang == 'ENG':
        order_params['Language'] = 'ENG'
    # extend_params_1 = {
    #     'ExpireDate': 7,
        # 'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
    #     'ClientRedirectURL': '',
    # }

    # extend_params_2 = {
    #     'StoreExpireDate': 15,
    #     'Desc_1': '',
    #     'Desc_2': '',
    #     'Desc_3': '',
    #     'Desc_4': '',
    #     'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
    #     'ClientRedirectURL': '',
    # }

    # extend_params_3 = {
    #     'BindingCard': 0,
    #     'MerchantMemberID': '',
    # }

    # extend_params_4 = {
    #     'Redeem': 'N',
    #     'UnionPay': 0,
    # }

    inv_params = {
        # 'RelateNumber': 'Tea0001', # 特店自訂編號
        # 'CustomerID': 'TEA_0000001', # 客戶編號
        # 'CustomerIdentifier': '53348111', # 統一編號
        # 'CustomerName': '客戶名稱',
        # 'CustomerAddr': '客戶地址',
        # 'CustomerPhone': '0912345678', # 客戶手機號碼
        # 'CustomerEmail': 'abc@ecpay.com.tw',
        # 'ClearanceMark': '2', # 通關方式
        # 'TaxType': '1', # 課稅類別
        # 'CarruerType': '', # 載具類別
        # 'CarruerNum': '', # 載具編號
        # 'Donation': '1', # 捐贈註記
        # 'LoveCode': '168001', # 捐贈碼
        # 'Print': '1',
        # 'InvoiceItemName': '測試商品1|測試商品2',
        # 'InvoiceItemCount': '2|3',
        # 'InvoiceItemWord': '個|包',
        # 'InvoiceItemPrice': '35|10',
        # 'InvoiceItemTaxType': '1|1',
        # 'InvoiceRemark': '測試商品1的說明|測試商品2的說明',
        # 'DelayDay': '0', # 延遲天數
        # 'InvType': '07', # 字軌類別
    }

    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID=os.environ.get("MERCHANT_ID"),
        HashKey=os.environ.get('HASH_KEY'),
        HashIV=os.environ.get("HASH_IV")
    )

    # 合併延伸參數
    # order_params.update(extend_params_1)
    # order_params.update(extend_params_2)
    # order_params.update(extend_params_3)
    # order_params.update(extend_params_4)

    # 合併發票參數
    # order_params.update(inv_params)

    try:
        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(order_params)
        check = ecpay_payment_sdk.generate_check_value(final_order_params)
        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        return html
    except Exception as error:
        print('An exception happened: ' + str(error))