from django.urls import include, path

from core.views import (
    DashboardTweets,
    KeywordFetchView,
    ProjectDetailView,
    ProjectView,
    UserDetailsView,
    UserLoginView,
    UserLogoutView,
    UserRegistrationView,
)
from lunarcrush.views import GetFeedsView, StreamLunarcrushFeedTweets
from twitter.views import ProjectTweetsListView

urlpatterns = [
    path("user/", UserDetailsView.as_view(), name="user-details"),
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
    path("dashboard/tweets/", DashboardTweets.as_view(), name="dashboard-tweets"),
    path("projects/", ProjectView.as_view()),
    path("lunar/feeds/", GetFeedsView.as_view(), name="lunarcrush-feeds"),
path("lunar/feeds/tweets/", StreamLunarcrushFeedTweets.as_view(), name="lunarcrush-feeds"),
    path("project/<int:pk>/", ProjectDetailView.as_view()),
    path(
        "projects/<int:project_id>/tweets/",
        ProjectTweetsListView.as_view(),
        name="project-tweets",
    ),
    path("twitter/", include("twitter.urls")),
]
