from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, write_transaction_to_firebase, update_account_balance, create_twqr_refund, create_refundFailed
from datetime import datetime, timedelta
import time
from .credit_detail_search import search_single_transaction
from .credit_do_action import perform_credit_do_action
import json

@csrf_exempt
def refund(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    auth_token = request.POST.get('auth_key')
    if not is_valid_token(auth_token):
        return HttpResponse('Unauthorized', status=401)
    
    current_time = datetime.now()
    if current_time.time() >= datetime.strptime('20:15', '%H:%M').time() and \
            current_time.time() <= datetime.strptime('20:30', '%H:%M').time():
        time.sleep((datetime.strptime('20:30', '%H:%M') - current_time.time()).total_seconds())
        return HttpResponseBadRequest("Cannot process request at this time")

    order_ids_str = request.POST.getlist('orderId', [])
    # order_id_list = json.loads(order_ids_str)
    order_ids_list = json.loads(order_ids_str[0])
    # print(order_ids_str)
    # order_ids_str = order_ids_str[0].strip("[]")  # Remove square brackets
    # order_id_list = [order_id.strip() for order_id in order_ids_str.split(",")]  # Split by comma and strip whitespace
    refundType = request.POST.get('refundType')
    print('Call the api successfully', order_ids_list, refundType)

    moneyReturn = 0
    for orderNo in order_ids_list:
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
            paymentMethod = tradeDetails.get('paymentMethod', '')
            tripRef = tradeDetails.get('tripRef', '')
        except Exception as e:
            print('Transaction data not found', e)
            create_refundFailed(user_ref, orderNo, tripRef)
            

        # return the money paid via wallet
        if moneyViaWallet > 0:
            if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) < startTime - current_time):
                moneyReturn += moneyViaWallet
            elif refundType == 'partial':
                moneyReturn += min(moneyViaWallet, totalCost * 0.5)

        print(moneyReturn)
        print(creditAmount)
        # return the money paid via credit

        if creditAmount > 0:
            if paymentMethod == 'ecpay':
                print('ecpay')
                try:
                    result = search_single_transaction(creditRefundId, creditAmount)
                    status = result['RtnValue']['status']
                except Exception as e:
                    print('An exception occurred while searching transaction:', e)
                    create_refundFailed(user_ref, orderNo, tripRef, refundType)
                    status = ''
                    

                try:
                    # full refund
                    if refundType == 'full': 
                        print('full')
                        if status == '已授權':
                            perform_credit_do_action(orderNo, tradeNo, creditAmount, action='N')
                        elif status == '要關帳':
                            perform_credit_do_action(orderNo, tradeNo, creditAmount, action='E')
                            perform_credit_do_action(orderNo, tradeNo, creditAmount, action='N')
                        elif status == '已關帳':
                            perform_credit_do_action(orderNo, tradeNo, creditAmount, action='R')
                        
                        tradeDetails['paymentStatus'] = 'cancelled'
                        tradeDetails['passengerCost'] = 0
                        tradeDetails['driverEarned'] = 0
                        write_transaction_to_firebase(orderNo, tradeDetails)
                    
                    # partial refund
                    elif refundType == 'partial' and moneyViaWallet <= totalCost *0.5:
                        print('partial')
                        refund_to_credit = calculate_refund_value(startTime, creditAmount, moneyViaWallet)
                        print(refund_to_credit)
                        if refund_to_credit > 0:
                            if status == '已授權':
                                perform_credit_do_action(orderNo, tradeNo, creditAmount, action='C')
                                perform_credit_do_action(orderNo, tradeNo, refund_to_credit, action='R')
                            elif status in ['要關帳', '已關帳']:
                                perform_credit_do_action(orderNo, tradeNo, refund_to_credit, action='R')
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = round(totalCost * 0.5)
                            tradeDetails['driverEarned'] = round(driverEarned * 0.35)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                        # cannot refund
                        else:
                            tradeDetails['driverEarned'] = round(driverEarned * 0.7)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                
                except Exception as e:
                    print('An exception occurred while refund ecpay:', e)
                    create_refundFailed(user_ref, orderNo, tripRef)

            elif paymentMethod == 'twqr':
                # full refund
                try: 
                    print('twqr')
                    if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) < startTime - current_time): 
                        tradeDetails['paymentStatus'] = 'cancelled'
                        tradeDetails['passengerCost'] = 0
                        tradeDetails['driverEarned'] = 0
                        write_transaction_to_firebase(orderNo, tradeDetails)
                        create_twqr_refund(user_ref, orderNo, creditAmount, 0, refundType, tripRef)
                    
                    # partial refund
                    elif refundType == 'partial' and moneyViaWallet <= totalCost *0.5:
                        refund_to_credit = calculate_refund_value(startTime, creditAmount, moneyViaWallet)
                        print(refund_to_credit)
                        if refund_to_credit > 0:
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = round(totalCost * 0.5)
                            tradeDetails['driverEarned'] = round(driverEarned * 0.35)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                            create_twqr_refund(user_ref, orderNo, refund_to_credit, totalCost - refund_to_credit - moneyViaWallet, refundType, tripRef)
                        # cannot refund
                        elif refund_to_credit == False:
                            tradeDetails['driverEarned'] = round(driverEarned * 0.7)
                            write_transaction_to_firebase(orderNo, tradeDetails)

                except Exception as e:
                    print('An exception occurred while refund twqr:', e)
                    create_refundFailed(user_ref, orderNo, tripRef)

        elif creditAmount == 0:
            if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) < startTime - current_time):
                tradeDetails['paymentStatus'] = 'cancelled'
                tradeDetails['passengerCost'] = 0
                tradeDetails['driverEarned'] = 0
                write_transaction_to_firebase(orderNo, tradeDetails)
            elif refundType == 'partial':
                start_timezone = startTime.tzinfo
                current_time = datetime.now(start_timezone)
                if timedelta(hours=24) < (startTime - current_time) < timedelta(hours=72):
                    tradeDetails['paymentStatus'] = 'cancelled'
                    tradeDetails['passengerCost'] = round(totalCost * 0.5)
                    tradeDetails['driverEarned'] = round(driverEarned * 0.35)
                    write_transaction_to_firebase(orderNo, tradeDetails)
                # cannot refund
                else:
                    tradeDetails['driverEarned'] = driverEarned * 0.7
                    write_transaction_to_firebase(orderNo, tradeDetails)

    if moneyReturn > 0:
        result = update_account_balance(user_ref, moneyReturn)
        if not result:
            create_refundFailed(user_ref, order_ids_list, tripRef)
            return HttpResponse('Refund Failed.')

    return HttpResponse('Refund processed successfully.')


def calculate_refund_value(startTime, credit_amount, money_via_wallet):
    start_timezone = startTime.tzinfo
    # Get the current time in the same timezone as startTime
    current_time = datetime.now(start_timezone)
    total = credit_amount + money_via_wallet
    if total * 0.5 >= money_via_wallet:
        if timedelta(hours=72) > startTime - current_time > timedelta(hours=24):
            refund = total * 0.5
            return round(refund)
    return False


import os
def is_valid_token(token):
    valid_tokens = [os.environ.get('API_AUTH_TOKEN')]
    return token in valid_tokens