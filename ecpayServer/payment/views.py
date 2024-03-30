from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .testEcpay import main
from functions.firebase import read_transaction_from_firebase

@csrf_exempt
def index(request):
    orderId = request.GET.get('orderId')
    if not orderId:
        return HttpResponseNotFound("Order ID not provided")

    result = read_transaction_from_firebase(orderId)

    if not result:
        return HttpResponseNotFound("Order not found")

    total_amount = result.get('price', 0)

    transaction_time = result.get('transactionTime', '')
    buyerId = result.get('user', '').id
    tripReference = result.get('tripReference') if result.get('tripReference') else ''
    print(tripReference, buyerId)

    return HttpResponse(main(total_amount, orderId, transaction_time, buyerId, tripReference))
