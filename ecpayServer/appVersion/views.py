from django.http import JsonResponse

def checkAppVersion(request):
    if request.method == 'POST':
        app_version = request.POST.get('app_version')
        platform = request.POST.get('platform')

        # Perform the app version check logic here
        # For simplicity, I'm assuming you have stored version numbers in a dictionary
        app_versions = {
            'ios': '1.0',
            'android': '1.0',
            'web': '1.0'
        }

        # Check if the requested platform and version match the stored version
        if platform in app_versions and app_versions[platform] == app_version:
            result = True  # Version matches
        else:
            result = False  # Version does not match

        # Return the result as JSON response
        return JsonResponse({'result': result})

    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'error': 'Invalid request method'}, status=400)