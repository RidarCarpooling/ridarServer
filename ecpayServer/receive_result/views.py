from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def receive_payment_info(request):
    if request.method == 'POST':
        # Extract parameters from the POST request
        merchant_id = request.POST.get('MerchantID')
        merchant_trade_no = request.POST.get('MerchantTradeNo')
        rtn_code = request.POST.get('RtnCode')
        rtn_msg = request.POST.get('RtnMsg')
        trade_no = request.POST.get('TradeNo')
        trade_amt = request.POST.get('TradeAmt')
        payment_type = request.POST.get('PaymentType')
        trade_date = request.POST.get('TradeDate')
        custom_field_1 = request.POST.get('CustomField1')
        check_mac_value = request.POST.get('CheckMacValue')
        print(rtn_msg, check_mac_value)

        # Perform additional processing if needed
        # For example, verify the integrity of the received data using CheckMacValue

        # Respond with a success message
        return HttpResponse('1|OK')
    else:
        # Return an error response for methods other than POST
        return HttpResponse('Method not allowed', status=405)
