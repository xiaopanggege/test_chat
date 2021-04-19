"""
ASGI config for test_chat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
#
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

# rest_framework_simplejwt解析token方法有点麻烦，也是直接看源码测试出来的
@database_sync_to_async
def get_user(token):
    try:
        validated_token = JWTAuthentication().get_validated_token(token)
        user = JWTAuthentication().get_user(validated_token)
        return user
    except Exception as e:
        return AnonymousUser()

class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        
        scope['user'] = await get_user(scope["query_string"])

        return await self.app(scope, receive, send)

QueryAuthMiddlewareStack = lambda inner: QueryAuthMiddleware(AuthMiddlewareStack(inner))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_chat.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": QueryAuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})