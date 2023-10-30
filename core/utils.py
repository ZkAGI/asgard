import json

import openai
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import permissions

from core.constants import OPEN_AI_APIKEY

User = get_user_model()


class StandardResponse(HttpResponse):
    def __init__(self, data=None, errors=None, status_code=200, headers=None):
        content = {
            "success": True if errors is None else False,
            "error": errors,
            "data": data,
        }
        super().__init__(
            content=json.dumps(content),
            status=status_code,
            content_type="application/json",
            headers=headers,
        )


class IsWhitelisted(permissions.BasePermission):
    """
    Custom permission to only allow whitelisted users to access the API.
    """

    def has_permission(self, request, view):
        return request.user.userprofile.is_whitelisted


def get_openai_content(keywords, rules):
    base_content = """You are an intelligent AI social media responder on behalf of a company.
You will be given a website landing page text and its brand domain link. Tweet reply text should not be bigger than 250 characters.
System is using the tweepy Python library to fetch relevant tweets.
System used these keywords(selected by user) to get tweets from Twitter: {}"""

    if not rules.strip():
        base_content += """
Rate between 1 to 10 for the relevancy of the tweet, where you should engage on this tweet on behalf of the company.
If rating is above 5, what would be your reply on the tweet. Else empty.
Return a JSON object as given format:
{
    "rate": 8.5,
    "reply_text": "reply_text"
}"""
    else:
        base_content += """
Rate between 1 to 10 for the relevancy of the tweet, where you should engage on this tweet on behalf of the company.
Return a JSON object as given format:
{
    "rate": 8.5
}"""
    return base_content.format(json.dumps(keywords))


def call_openai_api(messages, rules=""):
    openai.api_key = OPEN_AI_APIKEY
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=1.42,
        presence_penalty=1.52,
    )




def get_openai_response(tweet_text, soup_text, url, keywords, rules):
    # Set up your OpenAI API key here
    openai.api_key = OPEN_AI_APIKEY
    # Call the OpenAI API to get a response for the given text
    keywords_dump = json.dumps(keywords)
    content = """You are an intelligent AI Tweet generator on behalf of a company.
You will generate a reply for given posted tweet's text by some other twitter account, you will have to Rate between 1 to 10 for the relevancy of the given tweet text, if this tweet is relevent or not with given company's website details.

You will be given a following details:
1. website landing page text
2. brand domain link
3. tweet text posted by some other twitter account
4. Related keywords

Keep these rules in mind while generating reply:
tweet reply text should not be bigger than 250 characters. %s


Details:
1. Website Landing page text : %s
2. brand domain link : "%s"
3. Related keywords : "%s"


If rating is above 5, what would be your reply on the tweet. else empty.
Return a json object as given format
{
    \"rate\": 8.5,
    \"reply_text\":\"reply_text\"
}"""% (rules,soup_text,url,keywords_dump)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": content},
            {
                "role": "user",
                "content": '''Posted tweet text: "%s"''' % (tweet_text,)
            },
        ],
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=1.42,
        presence_penalty=1.52,
    )
    result = json.loads(response.choices[0]["message"]["content"])
    if "reply_text" in result.keys() and len(result["reply_text"]) > 250:
        return {
            "rate": 0,
            "message": "Generated reply exceeds 250 characters, so it's ignored.",
        }
    return result
