from django.http import JsonResponse

def parse_auth_headers(view):
    def wrapper(request, *args, **kwargs):
        try:
            user_id = request.headers.get('X-User-ID')
            user_email = request.headers.get('X-User-Email')
            user_name = request.headers.get('X_User-Name')
        except:
            return JsonResponse({"error": "Not Authorized"}, status=401)
        
        try:
            request.user_id = user_id
            request.user_name = user_name
            request.user_email = user_email
        except:
            return JsonResponse({"error": "Failure to add user attributes to request"}, status=500)
        
        return view(request, *args, **kwargs)
    return wrapper

