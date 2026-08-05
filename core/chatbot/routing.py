from django.urls import re_path
from .consumers import HumanChatConsumer

websocket_urlpatterns = [
    # USER (widget)
    re_path(
    r"ws/chat/(?P<widget_id>[^/]+)/(?P<email>[^/]+)/(?P<sender>[^/]+)/$",
    HumanChatConsumer.as_asgi(),
    ),


    # OWNER (dashboard)
    re_path(
    r"ws/chat/(?P<widget_id>[^/]+)/(?P<email>[^/]+)/(?P<sender>[^/]+)/$",
    HumanChatConsumer.as_asgi(),
    ),

]
