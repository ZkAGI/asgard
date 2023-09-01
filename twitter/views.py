from rest_framework.views import APIView

from core.models import Project
from twitter.serializers import FetchTweetRequestSerializer


# Create your views here.
class FetchTweetsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FetchTweetRequestSerializer(data=request.data)
        if serializer.is_valid():
            self.project = Project.objects.get(
                id=serializer.validated_data["project_id"]
            )
            self.keywords = self.project.keywords
        twtr_query = self.build_twitter_query(
            keywords=self.keywords,
            max_results=10,
            screen_name=self.request.user.username,
        )

    def build_twitter_query(keywords, max_results, screen_name):
        keywords = list(map(lambda x: f'"{x}"', keywords))
        query_str = f'({" OR ".join(keywords)})'
        # Append common filters
        query_str += f" -is:retweet -is:reply lang:en  -from:{screen_name}"
        # Build the query parameters dictionary
        query_params = {
            "query": query_str,
            "tweet.fields": "author_id,created_at",
            "user.fields": "name",
            "max_results": str(max_results),
        }
        return query_params
