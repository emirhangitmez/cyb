def bildirim_sayisi(request):
    if request.user.is_authenticated:
        return {"okunmamis_bildirim": request.user.bildirimler.filter(okundu=False).count()}
    return {}
