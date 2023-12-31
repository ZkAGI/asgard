import asyncio

from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import StandardResponse, IsWhitelisted
from listner.model import Scrape, Classifier, Intent
from listner.models import TGUser, Quest
from listner.serializers import TGUserSerializer, QuestSerializer


async def async_scrape_telegram(scraper, classifier, intent):
    df = await scraper.scrape_telegram()
    df['is_question'] = df['message'].apply(classifier.is_question)
    df2 = df.loc[df['is_question'] == True].copy()  # Create a copy of the slice

    # Use .loc to avoid SettingWithCopyWarning
    # df2.loc[:, 'is_of_value'] = df2['message'].apply(intent.intent)
    df2['is_of_value'] = df2['message'].apply(intent.intent)
    # df2.loc[:, 'is_narrow_filter'] = df2['message'].apply(intent.get_narrow_filter)
    df2['is_narrow_filter'] = df2['message'].apply(intent.get_narrow_filter)
    df2['is_relevant'] = None
    df2['has_responded'] = None

    # Convert Timestamp objects to string format
    if 'msg_date' in df2.columns:
        df2.loc[:, 'msg_date'] = df2['msg_date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

    return df2.to_dict(orient='records')


class IntentListnerView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        channel_list = data.get('channel_list', [])
        keywords_list = data.get('keywords_list', [])
        scraper = Scrape(channel_list)
        classifier = Classifier()
        intent = Intent(keywords_list)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        scraped_data = loop.run_until_complete(async_scrape_telegram(scraper, classifier, intent))
        loop.close()

        return StandardResponse(
            data=scraped_data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class IncentiviseListnerView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        channel_list = data.get('channel_list', [])
        keywords_list = data.get('keywords_list', [])
        quest_id = data.get("quest_id")
        scraper = Scrape(channel_list)
        classifier = Classifier()
        intent = Intent(keywords_list)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        scraped_data = loop.run_until_complete(async_scrape_telegram(scraper, classifier, intent))
        loop.close()

        for data in scraped_data:
            try:
                existing_record = TGUser.objects.get(userid=data['sender_id'], quest_id=quest_id)
                if existing_record is not None:
                    current_score = existing_record.score
                    existing_record.score = current_score + 1
                    existing_record.save()
            except:
                TGUser.objects.create(userid=data['sender_id'], score=1, quest_id=quest_id)
        return Response(data=scraped_data)


class TGUserListView(APIView):
    def get(self, request, quest_id, format=None):
        tg_users = TGUser.objects.all().filter(quest_id=quest_id).order_by('-score')
        serializer = TGUserSerializer(tg_users, many=True)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class QuestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def get(self, request, format=None):
        projects = Quest.objects.filter(user=request.user).order_by("created_at")
        paginator = PageNumberPagination()
        paginated_projects = paginator.paginate_queryset(projects, request)
        serializer = QuestSerializer(
            paginated_projects, context={"request": request}, many=True
        )

        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }

        return StandardResponse(
            data=response_data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request, format=None):
        serializer = QuestSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=request.user)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_201_CREATED,
        )
