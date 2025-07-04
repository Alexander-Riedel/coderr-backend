from django.urls import path
from .views import RegistrationView, LoginView


# URL patterns for authentication endpoints
urlpatterns = [
    # User registration endpoint: expects POST at /api/registration/
    path('registration/', RegistrationView.as_view(), name='registration'),

    # User login endpoint: expects POST at /api/login/
    path('login/', LoginView.as_view(), name='login'),
]
