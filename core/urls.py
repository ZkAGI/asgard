from django.urls import include, path

from core.views import (
    DashboardTweets,
    KeywordFetchView,
    ProjectDetailView,
    ProjectView,
    UserDetailsView,
    UserLoginView,
    UserLogoutView,
    UserRegistrationView, TrackedAccountView, TrackedDetailView,
)
from listner.views import IntentListnerView, IncentiviseListnerView, TGUserListView, QuestView
from lunarcrush.views import GetFeedsView, StreamLunarcrushFeedTweets
from tgotp.views import VerifyTelegram
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
    path('tracked-accounts/<int:project_id>/', TrackedDetailView.as_view(), name='tracked_account_details'),
    path('tracked-accounts/', TrackedAccountView.as_view(), name='tracked_account_details'),
    path("twitter/", include("twitter.urls")),
    path("listner/intent/", IntentListnerView.as_view(), name="intent-listner"),
    path("listner/incentivise/", IncentiviseListnerView.as_view(), name="incentivise-listner"),
    path('listner/leaderboard/<int:quest_id>/', TGUserListView.as_view(), name='tguser-list'),
    path('telegram/verify/', VerifyTelegram.as_view(), name='telegram-verify'),
    path('quest/', QuestView.as_view(), name='quest'),
]
