from django.urls import path

from twitter.views import (
    AccessTokenView,
    CheckTwitterView,
    PostTweetView,
    RequestOAuthView,
    StreamTweetsView,
    TweetDetailView,
    TwitterAccountDelete,
)

urlpatterns = [
    path("fetch-tweets/", StreamTweetsView.as_view(), name="fetch-tweets"),
    path("tweet/<int:pk>/", TweetDetailView.as_view(), name="tweet-detail"),
    path("post-tweet/", PostTweetView.as_view(), name="post-tweet"),
    path("request-token/", AccessTokenView.as_view(), name="request-token"),
    path("access-token/", RequestOAuthView.as_view(), name="access-token"),
    path("account/", CheckTwitterView.as_view(), name="check-account"),
    path("logout/", TwitterAccountDelete.as_view(), name="twitter-account-delete"),
]
