import json

import openai

OPEN_AI_APIKEY = "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"


def get_openai_response(tweet_text):
    # Set up your OpenAI API key here
    openai.api_key = OPEN_AI_APIKEY
    # Call the OpenAI API to get a response for the given text
    content = """You are an intelligent AI Tweet generator on behalf of a company.
    You will generate a reply for given posted tweet's text by some other twitter account, you will have to Rate between 1 to 10 for the relevancy of the given tweet text, if this tweet is relevant or not with given company's website details.

    You will be given the following details:
    1. Tweet Content: %s

    Keep these rules i-=n mind while generating a reply:
    The tweet reply text should not be bigger than 250 characters.

    Return a json object as given format
    {
        \"reply_text\":\"reply_text\"
    }""" % tweet_text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": '''Posted tweet text: "%s"''' % (tweet_text,)},
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

twt_text = """
#Bitcoin is building its legacy with strong roots in the world of finance. A decentralized revolution grounded in strength and resilience. 
"""
res = get_openai_response(twt_text)
print(res)