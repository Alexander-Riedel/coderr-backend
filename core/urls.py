"""
URL configuration for the Core Django project.

Routes include:
- Admin site
- API endpoints from each app (authentication, base info, profiles, offers, reviews, orders)
- Static media serving in DEBUG mode
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


# Root URL patterns for the project
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Authentication endpoints: registration and login
    path('api/', include('auth_app.api.urls')),

    # Aggregated base information endpoint
    path('api/', include('base_info_app.api.urls')),

    # Profile endpoints: CRUD operations for customer and business profiles
    path('api/', include('profile_app.api.urls')),

    # Offer endpoints: CRUD operations and detail retrieval
    path('api/', include('offers_app.api.urls')),

    # Review endpoints: CRUD operations for reviews
    path('api/', include('reviews_app.api.urls')),

    # Order endpoints: CRUD operations and count endpoints
    path('api/', include('orders_app.api.urls')),
]

# Serve media files (user-uploaded content) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
