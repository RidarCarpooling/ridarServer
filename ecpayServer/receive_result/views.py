from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def index(request):
    if request.method == 'POST':
        result = request.POST.get('RtnMsg')
        tid = request.POST.get('CustomField1')
        print(tid)
        # if trade_detail:
        #     trade_detail.status = '交易成功 sever post'
        #     trade_detail.save()
        return HttpResponse('1|OK')
        # else:
        #     return HttpResponse('Transaction not found', status=404)
    else:
        return HttpResponse('Method not allowed', status=405)
