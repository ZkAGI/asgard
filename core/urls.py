from django.urls import path

from core.views import UserLogoutView, UserRegistrationView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
]
