from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, write_transaction_to_firebase, update_account_balance, create_twqr_refund, create_refundFailed, get_email_and_name
from datetime import datetime, timedelta
import time
from .credit_detail_search import search_single_transaction
from .credit_do_action import perform_credit_do_action
import json
from functions.onesignal_send_email import send_refund_notification

@csrf_exempt
def refund(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    auth_token = request.POST.get('auth_key')
    if not is_valid_token(auth_token):
        return HttpResponse('Unauthorized', status=401)

    order_ids_str = request.POST.getlist('orderId', [])
    # order_id_list = json.loads(order_ids_str)
    order_ids_list = json.loads(order_ids_str[0])
    refundType = request.POST.get('refundType')
    print('Call the api successfully', order_ids_list, refundType)

    moneyReturnToWallet = 0
    totalReturn = 0
    passengers = 0
    for orderNo in order_ids_list:
        try:
            # finalPrice + moneyViaWallet == total passenger cost
            tradeDetails = read_transaction_from_firebase(orderNo)
            creditRefundId = tradeDetails.get('creditRefundId', '')
            creditAmount = tradeDetails.get('finalPrice', 0)
            tradeNo = tradeDetails.get('tradeNo', '')
            startTime = tradeDetails.get('startTime', '')
            finishTime = tradeDetails.get('finishTime', '')
            moneyViaWallet = tradeDetails.get('moneyViaWallet', 0)
            totalCost = tradeDetails.get('passengerCost', 0)
            driverEarned = tradeDetails.get('driverEarned', 0)
            user_ref = tradeDetails.get('user', '')
            driverName = tradeDetails.get('driverName', '')
            paymentMethod = tradeDetails.get('paymentMethod', '')
            paymentStatus = tradeDetails.get('paymentStatus', '')
            tripRef = tradeDetails.get('tripRef', '')
            startPlace = tradeDetails.get('startPlace', '')
            endPlace = tradeDetails.get("endPlace", '')
            num_of_passengers = tradeDetails.get('numOfPassengers', 0)
            passengers += num_of_passengers
        except Exception as e:
            print('Transaction data not found', e)
            create_refundFailed(user_ref, orderNo, tripRef)
            
        current_time = datetime.now()
        if current_time.time() >= datetime.strptime('20:15', '%H:%M').time() and \
                current_time.time() <= datetime.strptime('20:30', '%H:%M').time() and \
                paymentMethod == 'ecpay':
            create_refundFailed(user_ref, orderNo, tripRef)
            return HttpResponseBadRequest("Cannot process request at this time")

        start_timezone = startTime.tzinfo
        current_time = datetime.now(start_timezone)

        if paymentStatus != 'cancelled':
            # return the money paid via wallet
            if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) < startTime - current_time):
                if moneyViaWallet > 0:
                    moneyReturnToWallet += moneyViaWallet
                totalReturn += totalCost
            elif refundType == 'partial' and startTime - current_time > timedelta(hours=24):
                if moneyViaWallet > 0:
                    moneyReturnToWallet += min(moneyViaWallet, totalCost*0.5)
                totalReturn += totalCost*0.5

            print('moneyreturn: ', moneyReturnToWallet)
            print('creditAmount:', creditAmount)
            # return the money paid via credit

            if creditAmount > 0:
                if paymentMethod == 'ecpay':
                    print('ecpay')
                    if not ((startTime - current_time < timedelta(hours=24) and refundType == 'partial') or \
                            timedelta(hours=72) > startTime - current_time >= timedelta(hours=24) and moneyViaWallet >= totalCost*0.5):
                        try:
                            result = search_single_transaction(creditRefundId, creditAmount)
                            status = result['RtnValue']['status']
                        except Exception as e:
                            print('An exception occurred while searching transaction:', e)
                            if startTime - current_time > timedelta(hours=24):
                                create_refundFailed(user_ref, orderNo, tripRef, refundType)
                            status = ''
                        

                    try:
                        # full refund
                        if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) <= startTime - current_time): 
                            print('full')
                            try: 
                                if status == '已授權':
                                    perform_credit_do_action(orderNo, tradeNo, creditAmount, action='N')
                                elif status == '要關帳':
                                    perform_credit_do_action(orderNo, tradeNo, creditAmount, action='E')
                                    perform_credit_do_action(orderNo, tradeNo, creditAmount, action='N')
                                elif status == '已關帳':
                                    perform_credit_do_action(orderNo, tradeNo, creditAmount, action='R')
                            except Exception as e:
                                print('An exception occured while performing credit do action')
                                create_refundFailed(user_ref, orderNo, tripRef, refundType)
                            
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = 0
                            tradeDetails['driverEarned'] = 0
                            write_transaction_to_firebase(orderNo, tradeDetails)
                        
                        # partial refund
                        elif refundType == 'partial' and  timedelta(hours=72) > startTime - current_time >= timedelta(hours=24):
                            print('partial')
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = round(totalCost * 0.5)
                            tradeDetails['driverEarned'] = round(driverEarned * 0.35)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                            
                            if moneyViaWallet <= totalCost *0.5:
                                refund_to_credit = round(totalCost*0.5)
                                print('Refund to credit: ', refund_to_credit)
                                
                                try: 
                                    if refund_to_credit > 0:
                                        if status == '已授權':
                                            perform_credit_do_action(orderNo, tradeNo, creditAmount, action='C')
                                            perform_credit_do_action(orderNo, tradeNo, refund_to_credit, action='R')
                                        elif status in ['要關帳', '已關帳']:
                                            perform_credit_do_action(orderNo, tradeNo, refund_to_credit, action='R')
                                except Exception as e:
                                    print('An exception occured while performing credit do action')
                                    create_refundFailed(user_ref, orderNo, tripRef, refundType)
                                    
                        elif startTime - current_time < timedelta(hours=24) and refundType == 'partial':
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['driverEarned'] = round(driverEarned * 0.7)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                    
                    except Exception as e:
                        print('An exception occurred while refund ecpay:', e)
                        create_refundFailed(user_ref, orderNo, tripRef)


                elif paymentMethod == 'twqr':
                    # full refund
                    try: 
                        print('twqr')
                        if refundType == 'full' or (refundType == 'partial' and timedelta(hours=72) <= startTime - current_time): 
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = 0
                            tradeDetails['driverEarned'] = 0
                            write_transaction_to_firebase(orderNo, tradeDetails)
                            create_twqr_refund(user_ref, orderNo, 0, creditAmount, refundType, tripRef)
                        
                        elif timedelta(hours=72) > startTime - current_time >= timedelta(hours=24) and refundType == 'partial':
                            tradeDetails['paymentStatus'] = 'cancelled'
                            tradeDetails['passengerCost'] = round(totalCost * 0.5)
                            tradeDetails['driverEarned'] = round(driverEarned * 0.35)
                            write_transaction_to_firebase(orderNo, tradeDetails)
                            if moneyViaWallet <= totalCost *0.5:
                                refund_to_credit = round(totalCost*0.5)
                                create_twqr_refund(user_ref, orderNo, refund_to_credit, totalCost - refund_to_credit - moneyViaWallet, refundType, tripRef)
                        
                        elif startTime - current_time < timedelta(hours=24) and refundType == 'partial':
                                tradeDetails['paymentStatus'] = 'cancelled'
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
                        tradeDetails['paymentStatus'] = 'cancelled'
                        tradeDetails['driverEarned'] = driverEarned * 0.7
                        write_transaction_to_firebase(orderNo, tradeDetails)

    print('moneyReturnToWallet: ', moneyReturnToWallet)
    if moneyReturnToWallet > 0:
        result = update_account_balance(user_ref, moneyReturnToWallet)
        if not result:
            create_refundFailed(user_ref, order_ids_list, tripRef)
            return HttpResponse('Refund Failed.')

    

    email = request.POST.get('email', '')
    print(email)
    name = request.POST.get('name', '')
    user_id = request.POST.get('user_id', '')
    if email == ''  and user_id != '':
        email, name = get_email_and_name(user_id)

    if email != '' and email != False:
        send_refund_notification(name, email, totalReturn, order_ids_str, startTime, finishTime, driverName, startPlace, endPlace, passengers)
    return HttpResponse('Refund processed successfully.')



import os
def is_valid_token(token):
    valid_tokens = [os.environ.get('API_AUTH_TOKEN')]
    return token in valid_tokens