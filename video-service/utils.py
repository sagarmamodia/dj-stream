from fastapi.responses import JSONResponse

class JsonResponse:
    def __new__(cls, *args, **kwargs):
        response_dict = {}
        status=200

        for key in kwargs:
            if(key=="status"):
                status=kwargs.get(key)
                continue
            response_dict[key] = kwargs.get(key)

        return JSONResponse(response_dict, status_code=status)
        

obj = JsonResponse(error="Invalid statement", server="FastAPI", status=200)
print(type(obj))
