from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .testEcpay import main

@csrf_exempt
def index(request):
    return HttpResponse(main())