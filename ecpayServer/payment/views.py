from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .testEcpay import main

@csrf_exempt
def index(request):
    print(request.headers)
    totalAmount = request.GET.get('totalPrice')
    return HttpResponse(main(totalAmount))