from django.urls import path

from core.views import KeywordFetchView, UserLogoutView, UserRegistrationView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("core/fetch-keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
]
