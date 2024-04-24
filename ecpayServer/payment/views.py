from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .Ecpay import main
from functions.firebase import read_transaction_from_firebase
import time

@csrf_exempt
def index(request):
    orderId = request.GET.get('orderId')
    print(orderId)
    if not orderId:
        return HttpResponseNotFound("Order ID not provided")

    result = read_transaction_from_firebase(orderId)

    if not result:
        time.sleep(3) 
        result = read_transaction_from_firebase(orderId)
        print(result)
        if not result:
            return HttpResponseNotFound("Order not found")

    total_amount = result.get('finalPrice', 0)
    transaction_time = result.get('transactionTime', '')
    buyerId = result.get('user', '').id
    tripReference = result.get('tripRef', '')
    lang = result.get("ENG", '')

    return HttpResponse(main(total_amount, orderId, transaction_time, buyerId, tripReference.id, lang))
