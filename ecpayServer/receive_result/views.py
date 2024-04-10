from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, add_order_to_trip, update_transaction_data, add_trip_to_history, create_notifications_doc
from functions.gen_check import gen_check_mac_value
from functions.onesignal_send_email import send_notification
from functions.push_notification import trigger_push_notification
from datetime import timedelta
from .order_search import query_order

@csrf_exempt
def receive_payment_info(request):
    if request.method == 'POST':
        all_params = request.POST
        
        merchant_trade_no = request.POST.get('MerchantTradeNo')
        rtn_code = request.POST.get('RtnCode')
        trade_no = request.POST.get('TradeNo')
        check_mac_value = request.POST.get('CheckMacValue')

        result = read_transaction_from_firebase(merchant_trade_no)
        transaction_time = result.get('transactionTime', '')
        buyerRef = result.get('user', '')
        tripReference = result.get('tripRef', '')
        finish_time = result.get('finishTime', '')
        start_time = result.get('startTime', '')
        transaction_type = result.get('transactionType', '')
        num_of_passengers = result.get('numOfPassengers', 0)
        user_name = result.get('userName', '')
        lang = result.get("ENG", '')
        total_price = result.get('totalPrice', 0)
        final_price = result.get('finalPrice', 0)
        moneyViaWallet = result.get('moneyViaWallet', '')
        email = result.get('email', '')
        driverRef = result.get('userPaid', '')


        if transaction_type == 'success':
            included_users = [buyerRef, driverRef]
        else:
            included_users = [driverRef]
        
        checkMac = gen_check_mac_value(all_params)

        if (check_mac_value == checkMac):
            tradeResult = query_order(merchant_trade_no)
            credit_refund_id = tradeResult['gwsr']
            if ((rtn_code == '1' or rtn_code == 1) and tradeResult['TradeStatus'] == '1'):
                update_transaction_data(orderId=merchant_trade_no, transaction_data=result, paymentStatus='paid', tradeNo=trade_no, credit_refund_id=credit_refund_id)
                add_order_to_trip(tripReference, buyerRef, transaction_time, total_price, num_of_passengers, user_name, transaction_type, merchant_trade_no)
                add_trip_to_history(buyerRef, finish_time, tripReference, moneyViaWallet)
                create_notifications_doc(included_users, transaction_type, tripReference)
                if email != '':
                    send_notification(final_price, user_name, email)

                if transaction_type == 'success':
                    if lang == 'ENG':
                        trigger_push_notification(
                            notification_title="Successfully matched rideshare",
                            notification_text="A passenger has chosen your order. You can click on this message to view the order and get to know the passenger!",
                            user_refs=[driverRef.path],
                            notification_sound="default",
                            sender=buyerRef
                        )
                        trigger_push_notification(
                            notification_title="Reminder",
                            notification_text="The trip will depart in 2 hours, please pay attention to the time. (You can ignore this notification if you cancel your trip.)",
                            user_refs=[driverRef.path, buyerRef.path],
                            scheduled_time=start_time-timedelta(hours=2),
                            notification_sound="default",
                            sender=buyerRef
                        )

                    else:
                        trigger_push_notification(
                            notification_title="成功媒合共乘",
                            notification_text="有乘客選擇了您的訂單，可以點擊此訊息查看訂單，並且認識乘客！",
                            user_refs=[driverRef.path],
                            notification_sound="default",
                            sender=buyerRef
                        )
                        trigger_push_notification(
                            notification_title="貼心小提醒",
                            notification_text="您的旅程將於2小時後出發，請注意時間。(若您已取消旅程，可忽略此通知。)",
                            user_refs=[driverRef.path, buyerRef.path],
                            scheduled_time=start_time-timedelta(hours=2),
                            notification_sound="default",
                            sender=buyerRef
                        )
                else:
                    if lang == 'ENG':
                        trigger_push_notification(
                            notification_title="Rideshare request",
                            notification_text="There is a passenger asks to join your journey, agree as soon as possible!",
                            user_refs=[driverRef.path],
                            notification_sound="default",
                            sender=buyerRef
                        )
                    else:
                        trigger_push_notification(
                            notification_title="共乘請求",
                            notification_text="有乘客要求加入您的旅程，趕快去同意吧！",
                            user_refs=[driverRef.path],
                            notification_sound="default",
                            sender=buyerRef
                        )

            else: 
                update_transaction_data(orderId=merchant_trade_no, transaction_data=result, paymentStatus='failed', tradeNo=trade_no, credit_refund_id=None)
            return HttpResponse('1|OK')
        else:
            pass
    
    else:
        # Return an error response for methods other than POST
        return HttpResponse('Method not allowed', status=405)


