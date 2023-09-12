from django.urls import path

from twitter.views import (
    AccessTokenView,
    FetchTweetsView,
    PostTweetView,
    RequestOAuthView,
)

urlpatterns = [
    path("tweets/", FetchTweetsView.as_view(), name="fetch-tweets"),
    path("tweet/", PostTweetView.as_view(), name="post-tweet"),
    path("request-token/", AccessTokenView.as_view(), name="request-token"),
    path("access-token/", RequestOAuthView.as_view(), name="access-token"),
]
