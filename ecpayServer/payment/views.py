from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .testEcpay import main

@csrf_exempt
def index(request):
    allowed_referrer = ["https://ridar.com.tw", 'https://vercel.com/']  # Replace with the URL of the specific website

    # Check if the request has a referrer
    try:
        print(request.META.get("HTTP_REFERER"))
    except:
        pass
    
    if 'HTTP_REFERER' in request.META:
        referrer = request.META['HTTP_REFERER']
        print(referrer)

        # Check if the referrer matches the allowed referrer
        if referrer != allowed_referrer:
            return HttpResponseForbidden("Access Forbidden: You are not authorized to access this page.")

    else:
        # No referrer provided, deny access
        return HttpResponseForbidden("Access Forbidden: You are not authorized to access this page.")
    totalAmount = request.GET.get('totalPrice')
    print(totalAmount)
    return HttpResponse(main(totalAmount))