import asyncio

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView

from core.utils import StandardResponse
from listner.model import Scrape, Classifier, Intent
from listner.models import TGUser
from listner.serializers import TGUserSerializer


# Create your views here.

async def async_scrape_telegram(scraper, classifier, intent):
    df = await scraper.scrape_telegram()
    df['is_question'] = df['message'].apply(classifier.is_question)
    df2 = df[df['is_question'] == True]
    df2['is_of_value'] = df2['message'].apply(intent.intent)
    df2['is_narrow_filter'] = df2['message'].apply(intent.get_narrow_filter)
    df2['is_relevant'] = None
    df2['has_responded'] = None

    # Convert Timestamp objects to string format
    if 'msg_date' in df2.columns:
        df2['msg_date'] = df2['msg_date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

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
        scraper = Scrape(channel_list)
        classifier = Classifier()
        intent = Intent(keywords_list)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        scraped_data = loop.run_until_complete(async_scrape_telegram(scraper, classifier, intent))
        loop.close()

        for data in scraped_data:
            try:
                existing_record = TGUser.objects.get(userid=data['sender_id'])
                if existing_record is not None:
                    current_score = existing_record.score
                    existing_record.score = current_score + 1
                    existing_record.save()
            except:
                TGUser.objects.create(userid=data['sender_id'], score=1)

        return StandardResponse(
            data=scraped_data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class TGUserListView(APIView):
    def get(self, request, format=None):
        tg_users = TGUser.objects.all().order_by('-score')
        serializer = TGUserSerializer(tg_users, many=True)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )