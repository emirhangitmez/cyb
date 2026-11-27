from .models import Rol


def kullanici_bilgisi(request):
    return {"Rol": Rol}
