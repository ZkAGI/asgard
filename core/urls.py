from django.urls import include, path

from core.views import (
    DashboardTweets,
    KeywordFetchView,
    ProjectCreateView,
    ProjectDetailView,
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
    path("keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
    path("dashboard/tweets/", DashboardTweets.as_view(), name="dashboard-tweets"),
    path("projects/", ProjectCreateView.as_view()),
    path("project/<int:pk>/", ProjectDetailView.as_view()),
    path("twitter/", include("twitter.urls")),
]
