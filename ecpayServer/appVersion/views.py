from django.http import JsonResponse

def checkAppVersion(request):
    # Latest versions for each platform
    latest_versions = {
        'ios': '1.0',
        'android': '1.0',
        'web': '1.0'
    }

    # Get app version and platform from the request
    app_version = request.POST.get('app_version')
    platform = request.POST.get('platform')

    # Check if the platform and app version are provided
    if app_version and platform:
        # Check if the platform exists in the latest_versions dictionary
        if platform in latest_versions:
            latest_version = latest_versions[platform]
            
            # Compare the client version with the latest version
            if app_version < latest_version:
                # If the client version is outdated, return True
                return JsonResponse({'upgrade_required': True})
            else:
                # If the client version is up-to-date, return False
                return JsonResponse({'upgrade_required': False})
        else:
            # If the platform is not supported, return an error
            return JsonResponse({'error': f'Unsupported platform: {platform}'}, status=400)
    else:
        # If app_version or platform is missing, return an error
        return JsonResponse({'error': 'App version and platform are required'}, status=400)
