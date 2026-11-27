from .models import Yetki


def kullanici_bilgisi(request):
    return {"Yetki": Yetki}
