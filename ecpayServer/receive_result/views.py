from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from functions.firebase import read_transaction_from_firebase, write_transaction_to_firebase
from functions.gen_check import genCheckMacValue

@csrf_exempt
def receive_payment_info(request):
    if request.method == 'POST':
        merchant_trade_no = request.POST.get('MerchantTradeNo')
        rtn_code = request.POST.get('RtnCode')
        trade_no = request.POST.get('TradeNo')
        trade_amt = request.POST.get('TradeAmt')
        payment_type = request.POST.get('PaymentType')
        check_mac_value = request.POST.get('CheckMacValue')

        result = read_transaction_from_firebase(merchant_trade_no)
        total_amount = result.get('price', 0)
        transaction_time = result.get('transactionTime', '')
        buyerId = result.get('user', '')
        tripReference = result.get('tripId', '')

        checkMac = genCheckMacValue(merchant_trade_no, transaction_time, total_amount, buyerId, tripReference)
        print(check_mac_value == checkMac)
        print(checkMac)

        if (rtn_code == 1 and check_mac_value == checkMac):
            print('matching')
            # update transaction: status, trade_no, create docs, and ....


        return HttpResponse('1|OK')
    else:
        # Return an error response for methods other than POST
        return HttpResponse('Method not allowed', status=405)
