# SEEVAL_api/middleware.py

class simple_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("=== Incoming request headers ===")
        for header, value in request.headers.items():
            print(f"{header}: {value}")
        response = self.get_response(request)
        return response
