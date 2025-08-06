from drf_yasg import openapi
from django.contrib import admin
from .views import api_root_view
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
# from debug_toolbar.toolbar import debug_toolbar_urls



schema_view = get_schema_view(
   openapi.Info(
      title="BookHeaven - Library Management API",
      default_version='v1',
      description="API documentation for Library Management System.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@bookheaven.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root_view),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/v1/', include('api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
# + debug_toolbar_urls()
