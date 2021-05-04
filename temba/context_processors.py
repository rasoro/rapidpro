from django.conf import settings


def branding(request):
    """
    Stuff our branding into the context
    """
    if "vanilla" in request.GET:
        request.session["vanilla"] = request.GET.get("vanilla")

    return dict(brand=request.branding, vanilla=request.session.get("vanilla", "0") == "1")


def analytics(request):
    """
    Stuffs intercom / segment / google analytics settings into our request context
    """
    return dict(
        segment_key=settings.SEGMENT_IO_KEY,
        intercom_app_id=settings.INTERCOM_APP_ID,
        google_tracking_id=settings.GOOGLE_TRACKING_ID,
    )


def enable_weni_layout(request):

    host = request.get_host().split(":")[0]

    return {"use_weni_layout": host.endswith(settings.WENI_DOMAINS["weni"])}


def weni_announcement(request):
    return {
        "announcement_left": settings.ANNOUNCEMENT_LEFT,
        "announcement_right": settings.ANNOUNCEMENT_RIGHT,
        "announcement_link": settings.ANNOUNCEMENT_LINK,
        "announcement_button": settings.ANNOUNCEMENT_BUTTON,
    }


def hotjar(request):
    return {
        "hotjar_id": settings.HOTJAR_ID
    }
