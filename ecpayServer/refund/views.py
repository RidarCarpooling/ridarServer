from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, write_transaction_to_firebase
from datetime import datetime, timedelta
import time
from .credit_detail_search import search_single_transaction
from .credit_do_action import perform_credit_do_action

@csrf_exempt
def refund(request):
    current_time = datetime.now()
    if current_time.time() >= datetime.strptime('20:15', '%H:%M').time() and \
            current_time.time() <= datetime.strptime('20:30', '%H:%M').time():
        time.sleep((datetime.strptime('20:30', '%H:%M') - current_time.time()).total_seconds())

    orderId = request.POST.get('orderId')
    refundType = request.POST.get('refundType')
    print('Call the api successfully', orderId, refundType)

    try:
        tradeDetails = read_transaction_from_firebase(orderId)
        creditRefundId = tradeDetails.get('creditRefundId', '')
        creditAmount = tradeDetails.get('finalPrice', '')
        tradeNo = tradeDetails.get('tradeNo', '')
        startTime = tradeDetails.get('startTime', '')
        moneyViaWallet = tradeDetails.get('moneyViaWallet', '')
    except Exception as e:
        print('Transaction data not found', e)

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
        elif refundType == 'partial':
            refund_value = calculate_refund_value(startTime, creditAmount, moneyViaWallet)
            if refund_value:
                if status == '已授權':
                    perform_credit_do_action(orderId, tradeNo, creditAmount, action='C')
                    perform_credit_do_action(orderId, tradeNo, refund_value, action='R')
                elif status in ['要關帳', '已關帳']:
                    perform_credit_do_action(orderId, tradeNo, refund_value, action='R')
                tradeDetails['paymentStatus'] = 'cancelled'
                tradeDetails['passengerCost'] = (creditAmount + moneyViaWallet) * 0.5
                tradeDetails['driverEarned'] = (creditAmount + moneyViaWallet) * 0.35
                write_transaction_to_firebase(orderId, tradeDetails)
            # cannot refund
            else:
                tradeDetails['driverEarned'] = (creditAmount + moneyViaWallet) * 0.7
                write_transaction_to_firebase(orderId, tradeDetails)
    
    return HttpResponse('Method not allowed', status=405)

def calculate_refund_value(startTime, credit_amount, money_via_wallet):
    total = credit_amount + money_via_wallet
    if total * 0.5 >= money_via_wallet:
        if timedelta(hours=72) > startTime - datetime.now() > timedelta(hours=24):
            refund = total * 0.5 + money_via_wallet
            return refund
    return False
