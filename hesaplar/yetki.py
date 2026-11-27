from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def rol_gerekli(*roller):
    """Görünüme sadece belirtilen rollerdeki kullanıcıların girmesine izin verir."""

    def dekorator(gorunum):
        @wraps(gorunum)
        @login_required
        def sarmal(request, *args, **kwargs):
            if request.user.rol not in roller:
                raise PermissionDenied("Bu sayfa için yetkiniz yok.")
            return gorunum(request, *args, **kwargs)

        return sarmal

    return dekorator
