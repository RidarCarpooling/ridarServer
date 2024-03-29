from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
def clientResult(request):
    if request.method == 'POST':
        # Extract parameters from the POST request
        rtn_code = request.POST.get('RtnCode')
        check_mac_value = request.POST.get('CheckMacValue')
        print(rtn_code, check_mac_value)

        # Perform additional processing if needed
        # For example, verify the integrity of the received data using CheckMacValue

        # Check the value of rtn_code
        if rtn_code == '1':
            # Payment succeeded, return a response with a success message
            return render(request, 'paymentSuccessed.html')
        else:
            # Payment failed, return a response with an error message
            return render(request, 'paymentFailed.html')
        
    else:
        # Return an error response for methods other than POST
        return HttpResponse('Method not allowed', status=405)
