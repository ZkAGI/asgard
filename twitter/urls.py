from django.urls import path

from twitter.views import (
    AccessTokenView,
    FetchTweetsView,
    PostTweetView,
    RequestOAuthView,
    TweetDetailView,
)

urlpatterns = [
    path("fetch-tweets/", FetchTweetsView.as_view(), name="fetch-tweets"),
    path("tweet/<int:pk>/", TweetDetailView.as_view(), name="tweet-detail"),
    path("post-tweet/", PostTweetView.as_view(), name="post-tweet"),
    path("request-token/", AccessTokenView.as_view(), name="request-token"),
    path("access-token/", RequestOAuthView.as_view(), name="access-token"),
]