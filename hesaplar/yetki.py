from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def rol_gerekli(*roller):
    """Görünüme sadece belirtilen yetki seviyesindeki kullanıcıların girmesine izin verir."""

    def dekorator(gorunum):
        @wraps(gorunum)
        @login_required
        def sarmal(request, *args, **kwargs):
            if request.user.rol not in roller:
                raise PermissionDenied("Bu sayfa için yetkiniz yok.")
            return gorunum(request, *args, **kwargs)

        return sarmal

    return dekorator


def admin_gerekli(gorunum):
    @wraps(gorunum)
    @login_required
    def sarmal(request, *args, **kwargs):
        if not request.user.admin_mi:
            raise PermissionDenied("Bu sayfa sadece admin içindir.")
        return gorunum(request, *args, **kwargs)

    return sarmal
