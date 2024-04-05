from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, write_transaction_to_firebase, update_account_balance
from datetime import datetime, timedelta
import time
from .credit_detail_search import search_single_transaction
from .credit_do_action import perform_credit_do_action

@csrf_exempt
def refund(request):

    authorization_token = request.headers.get('Authorization')
    if not is_valid_token(authorization_token):
        return HttpResponse('Unauthorized', status=401)
    
    current_time = datetime.now()
    if current_time.time() >= datetime.strptime('20:15', '%H:%M').time() and \
            current_time.time() <= datetime.strptime('20:30', '%H:%M').time():
        time.sleep((datetime.strptime('20:30', '%H:%M') - current_time.time()).total_seconds())

    orderId = request.POST.getlist('orderId', [])
    refundType = request.POST.get('refundType')
    print('Call the api successfully', orderId, refundType)

    moneyReturn = 0
    for orderNo in orderId:
        try:
            # finalPrice + moneyViaWallet == total passenger cost
            tradeDetails = read_transaction_from_firebase(orderNo)
            creditRefundId = tradeDetails.get('creditRefundId', '')
            creditAmount = tradeDetails.get('finalPrice', 0)
            tradeNo = tradeDetails.get('tradeNo', '')
            startTime = tradeDetails.get('startTime', '')
            moneyViaWallet = tradeDetails.get('moneyViaWallet', 0)
            totalCost = tradeDetails.get('passengerCost', 0)
            driverEarned = tradeDetails.get('driverEarned', 0)
            user_ref = tradeDetails.get('user', '')
        except Exception as e:
            print('Transaction data not found', e)

        # return the money paid via wallet
        if moneyViaWallet > 0:
            if refundType == 'full':
                moneyReturn += moneyViaWallet
            elif refundType == 'partial':
                moneyReturn += min(moneyViaWallet, totalCost * 0.5)

        # return the money paid via credit
        if creditAmount > 0:
            try:
                result = search_single_transaction(creditRefundId, creditAmount)
                status = result['RtnValue']['status']
            except Exception as e:
                print('An exception occurred while searching transaction:', e)
                status = ''

            # full refund
            if refundType == 'full': 
                if status == '已授權':
                    perform_credit_do_action(orderId, tradeNo, creditAmount, action='N')
                elif status == '要關帳':
                    perform_credit_do_action(orderId, tradeNo, creditAmount, action='E')
                    perform_credit_do_action(orderId, tradeNo, creditAmount, action='N')
                elif status == '已關帳':
                    perform_credit_do_action(orderId, tradeNo, creditAmount, action='R')
                
                tradeDetails['paymentStatus'] = 'cancelled'
                tradeDetails['passengerCost'] = 0
                tradeDetails['driverEarned'] = 0
                write_transaction_to_firebase(orderId, tradeDetails)
            
            # partial refund
            elif refundType == 'partial' and moneyViaWallet <= totalCost *0.5:
                refund_to_credit = calculate_refund_value(startTime, creditAmount, moneyViaWallet)
                if refund_to_credit > 0:
                    if status == '已授權':
                        perform_credit_do_action(orderId, tradeNo, creditAmount, action='C')
                        perform_credit_do_action(orderId, tradeNo, refund_to_credit, action='R')
                    elif status in ['要關帳', '已關帳']:
                        perform_credit_do_action(orderId, tradeNo, refund_to_credit, action='R')
                    tradeDetails['paymentStatus'] = 'cancelled'
                    tradeDetails['passengerCost'] = totalCost * 0.5
                    tradeDetails['driverEarned'] = driverEarned * 0.35
                    write_transaction_to_firebase(orderId, tradeDetails)
                # cannot refund
                else:
                    tradeDetails['driverEarned'] = driverEarned * 0.7
                    write_transaction_to_firebase(orderId, tradeDetails)
        
    if moneyReturn > 0:
        update_account_balance(user_ref, moneyReturn)

    return HttpResponse('Method not allowed', status=405)


def calculate_refund_value(startTime, credit_amount, money_via_wallet):
    total = credit_amount + money_via_wallet
    if total * 0.5 >= money_via_wallet:
        if timedelta(hours=72) > startTime - datetime.now() > timedelta(hours=24):
            refund = total * 0.5 + money_via_wallet
            return refund
    return False

import os

def is_valid_token(token):
    valid_tokens = [os.environ.get('API_AUTH_TOKEN')]
    return token in valid_tokens