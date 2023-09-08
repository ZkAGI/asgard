from django.urls import path

from core.views import (
    DashboardTweets,
    KeywordFetchView,
    UserLogoutView,
    UserRegistrationView,
)
from twitter.views import (
    AccessTokenView,
    FetchTweetsView,
    PostTweetView,
    RequestOAuthView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("core/keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
    path("twitter/tweets/", FetchTweetsView.as_view(), name="fetch-tweets"),
    path("twitter/tweet/", PostTweetView.as_view(), name="post-tweet"),
    path("dashboard/tweets/", DashboardTweets.as_view(), name="dashboard-tweets"),
    path("twitter/request-token/", AccessTokenView.as_view(), name="request-token"),
    path("twitter/access-token/", RequestOAuthView.as_view(), name="access-token"),
]
