from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def refund(request):
    return HttpResponse('Method not allowed', status=405)

