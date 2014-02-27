from django.conf import settings

def app_data(request):
    return {
        'app_name': getattr(settings, 'APP_NAME', 'StatKeeper')
    }