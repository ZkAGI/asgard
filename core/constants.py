EMAIL_REGEX = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
OPEN_AI_INSTRUCTION = "You are a intelligent AI. You are given a website landing page text and its brand domain link. We are using tweepy python library to fetch relevant tweets about this domain brand.\nYou will suggest keywords(as list) which can be used in tweepy library (python) to filter tweets stream to get relevant tweets for this brand.\n\nSuggests top 10 keywords.\n\n Never ever use company name as keywords( Follow this instruction strictly )"
OPEN_AI_APIKEY = "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"
HEADERS = {
    "authority": "rejolut.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.google.com/",
    "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
}
