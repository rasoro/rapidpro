from django.conf import settings


def use_weni_layout(request):

    host = request.get_host().split(":")[0]
    in_weni = host.endswith(settings.WENI_DOMAINS["weni"])
    in_iframe = request.headers.get("Sec-Fetch-Dest") == "iframe"

    return {"use_weni_layout": in_weni and in_iframe}


def show_sidemenu(request):
    if request.path == "/":
        return {"show_sidemenu": False}

    for path in settings.SIDEBAR_EXCLUDE_PATHS:
        if path in request.path:
            return {"show_sidemenu": False}

    return {"show_sidemenu": True}


def weni_announcement(request):
    return {
        "announcement_left": settings.ANNOUNCEMENT_LEFT,
        "announcement_right": settings.ANNOUNCEMENT_RIGHT,
        "announcement_link": settings.ANNOUNCEMENT_LINK,
        "announcement_button": settings.ANNOUNCEMENT_BUTTON,
    }


def hotjar(request):
    return {"hotjar_id": settings.HOTJAR_ID}
