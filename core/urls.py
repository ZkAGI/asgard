from django.urls import path

from core.views import KeywordFetchView, UserLogoutView, UserRegistrationView
from twitter.views import FetchTweetsView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("core/keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
    path("twitter/tweets/", FetchTweetsView.as_view(), name="fetch-tweets"),
]
