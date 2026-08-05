import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 🔴 THIS WAS MISSING — THIS IS THE FIX
django.setup()

import chatbot.routing  # ← SAFE NOW

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(chatbot.routing.websocket_urlpatterns)
    ),
})
