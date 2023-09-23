from django.urls import include, path

from core.views import (
    DashboardTweets,
    KeywordFetchView,
    ProjectDetailView,
    ProjectView,
    UserLogoutView,
    UserRegistrationView, UserDetailsView,
)

urlpatterns = [
    path("user/", UserDetailsView.as_view(), name="user-details"),
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("keywords/", KeywordFetchView.as_view(), name="fetch-keywords"),
    path("dashboard/tweets/", DashboardTweets.as_view(), name="dashboard-tweets"),
    path("projects/", ProjectView.as_view()),
    path("project/<int:pk>/", ProjectDetailView.as_view()),
    path("twitter/", include("twitter.urls")),
]
