from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import message.routing
from message.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": JWTAuthMiddleware(
        URLRouter(
            message.routing.websocket_urlpatterns
        )
    ),
})