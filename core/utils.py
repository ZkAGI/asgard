import json

import openai
from django.contrib.auth import get_user_model
from django.http import HttpResponse

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
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.67,
        max_tokens=2431,
        top_p=1,
        frequency_penalty=1.42,
        presence_penalty=1.52,
    )


def get_openai_response(tweet_text, soup_text, url, keywords, rules):
    # Set up your OpenAI API key here
    openai.api_key = OPEN_AI_APIKEY
    # Call the OpenAI API to get a response for the given text
    content = (
        """You are an intelligent AI social media responder on behalf of a company.
                You are given a tweet's text and you will have to decide if this tweet is relevent or not with given company details.
You will be given a website landing page text and its brand domain link. tweet reply text should not be bigger than 250 characters.
System is using the tweepy python library to fetch relevant tweets.
System used these keywords(selected by user) to get tweets from twitter: """
        + json.dumps(keywords)
        + """

Rate between 1 to 10 for the relevancy of the tweet, where you should engage on this tweet on behalf of the company.
Return a json object as given format
{
    \"rate\": 8.5,
}"""
    )
    if not rules.strip():
        content = (
            """You are an intelligent AI social media responder on behalf of a company.
                You are given a tweet's text and you will have to decide if this tweet is relevent or not with given company details.
You will be given a website landing page text and its brand domain link. tweet reply text should not be bigger than 250 characters.
System is using the tweepy python library to fetch relevant tweets.
System used these keywords(selected by user) to get tweets from twitter: """
            + json.dumps(keywords)
            + """

Rate between 1 to 10 for the relevancy of the tweet, where you should engage on this tweet on behalf of the company.
If rating is above 5, what would be your reply on the tweet. else empty.
Return a json object as given format
{
    \"rate\": 8.5,
    \"reply_text\":\"reply_text\"
}"""
        )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": content},
            {
                "role": "user",
                "content": f"Domain: {url}\nlanding page text: {soup_text.strip()} \n Analyze this tweet data:\n "
                + json.dumps({"tweet_text": tweet_text}),
            },
            {
                "role": "user",
                "content": json.dumps({"author_name": "", "tweet_text": tweet_text}),
            },
        ],
        temperature=0.67,
        max_tokens=2431,
        top_p=1,
        frequency_penalty=1.42,
        presence_penalty=1.52,
    )
    result = json.loads(response.choices[0]["message"]["content"])

    if not rules.strip():
        return result
    rate_value = int(result["rate"])
    if rate_value > 5:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": """You are an smart intelligent AI social media responder on behalf of a twitter page.
        What would be your reply on the tweet. else empty. tweet reply text should not be bigger than 250 characters.
        Return a json object as given format
        {
            \"reply_text\":\"reply_text\"
        }"""
                    + f'\n\nuse these rules when you write "reply_text":\n{rules}',
                },
                {
                    "role": "user",
                    "content": "give me reply text json object for this tweet data:\n"
                    + json.dumps({"tweet_text": tweet_text}),
                },
            ],
            temperature=0.67,
            max_tokens=2431,
            top_p=1,
            frequency_penalty=1.42,
            presence_penalty=1.52,
        )
        try:
            result = json.loads(response.choices[0]["message"]["content"])
        except Exception as e:
            return get_openai_response(tweet_text, soup_text, url, keywords, rules)

    result["rate"] = rate_value

    return result
