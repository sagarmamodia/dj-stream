from fastapi.responses import JSONResponse
import uuid

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
        

# obj = JsonResponse(error="Invalid statement", server="FastAPI", status=200)
# print(type(obj))

def is_valid_uuid(string):
    try:
        uuid_string = uuid.UUID(string)
        return True
    except:
        return False

