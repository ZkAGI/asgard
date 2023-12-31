import datetime
import pickle

import discum
import nltk
import pandas as pd
import pymongo
import pytz
import requests
from dateutil import parser
import os
from pytz import timezone
from telethon.sync import TelegramClient

nltk.download('punkt')

class Scrape:
    """

    Class to scrape messages from telegram and discord

    """

    def __init__(self, channel_list):
        """
        Constructor for scrape class takes api credentials for telegram api and also the list of telegram channels and discord cahnnels.

        """

        # seema sinha
        base_dir = os.path.abspath(os.path.dirname(__file__))
        self.name = os.path.join(base_dir, 'listener.session')
        self.api_id = 21647307
        self.api_hash = '02d86acbfaa3a90dc031b35559287632'

        self.channel_list = channel_list
        self.discord_channel_list = {'optimism': "667044844366987296", 'binance_global-chat': "882554401154289667",
                                     'cronos': "941029206995910781", 'binance_help': "964179447152537641",
                                     'apeSwap_general': "821817978726645763", 'apeSwap_support': "825226547744473119",
                                     'apeSwap_polygon': "856561376196558878", 'apeSwap_degen': "825231962549387306"}

    async def scrape_telegram(self):
        """
        This function scrapes messages from Telegram asynchronously.
        """
        message = []
        message_id = []
        channel_name = []
        msg_date = []
        sender_id = []
        async with TelegramClient(self.name, self.api_id, self.api_hash) as client:
            tzinfo = datetime.timezone.utc
            date = datetime.datetime.now(tzinfo)
            hour_back = date - datetime.timedelta(hours=1)
            for i in self.channel_list:
                async for msg in client.iter_messages(i, limit=200, offset_date=date):
                    if msg.date > hour_back:
                        message.append(msg.text)
                        sender_id.append(msg.from_id.user_id)
                        message_id.append(msg.id)
                        channel_name.append(i)
                        msg_date.append(msg.date.astimezone(timezone('Asia/Kolkata')) + datetime.timedelta(hours=5, minutes=30))

            df = pd.DataFrame({"message": message, "message_id": message_id,
                               "channel_name": channel_name, "sender_id": sender_id})
            df['platform'] = 'Telegram'
            return df

    def scrape_discord(self):
        """
        This function scrapes the messags from Discord.

        """
        message = []
        message_id = []
        channel_name = []
        msg_date = []
        bot = discum.Client(email='surajvenkat000@gmail.com', password="bitbaza@123",
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                            log={'console': False, 'file': False},
                            token="ODg4ODU3NTg2NDAzODAzMTU4.G693RX.q4eH69J--0cG3q-IVOW0Nwv1yjGkyxIT0mDO2o")
        # messages = bot.getMessages(channel_id,num=100).json()
        tzinfo = datetime.timezone.utc
        date = datetime.datetime.now(tzinfo)
        # utc=pytz.UTC
        hour_after = date + datetime.timedelta(hours=1)
        # time from when the scrape.
        hour_back = date - datetime.timedelta(hours=1)
        for i, k in self.discord_channel_list.items():
            messages = bot.getMessages(k, num=100).json()
            for j in messages:
                # parse the message date as it is in string format.
                try:
                    d1 = parser.parse(j['timestamp'])
                except:
                    pass
                if d1 > hour_back:
                    message.append(j['content'])
                    message_id.append(j['id'])
                    channel_name.append(i)
                    # append time after converting it into IST + 5:30, so that mongoDB recognises date correctly.
                    msg_date.append(d1.astimezone(timezone(
                        'Asia/Kolkata')) + datetime.timedelta(hours=5) + datetime.timedelta(minutes=30))

        df = pd.DataFrame({"message": message, "message_id": message_id,
                           "channel_name": channel_name, "msg_date": msg_date})
        df['platform'] = 'Discord'
        #        df.to_csv("test3.csv", index=False)
        return df

    def send_update(self, length):
        """
        This function send update to the client at their telegram id.

        """
        with TelegramClient(self.name, self.api_id, self.api_hash) as client:
            client.send_message(entity='enter_name_here', message=str(
                length) + " new updates on social listener dashboard")

            # TO-DO: Implement messaging sending to group of owner.


class Classifier:
    """

    Class to classify questions out of all the messages sent on various channels.

    """

    def __init__(self):
        """
        Constructor for classifier class. Takes few important parameters as well as loads a pre-trained "my_classifier.pickle" classifier.
        """
        self.question_types = ["whQuestion", "ynQuestion"]
        self.question_pattern = ["do i", "do you", "what", "who", "is it", "why", "would you", "how", "is there",
                                 "are there", "is it so", "is this true", "to know", "is that true", "are we", "am i",
                                 "question is", "tell me more", "can i", "can we", "tell me", "can you explain",
                                 "question", "answer", "questions", "answers", "ask"]

        self.helping_verbs = ["is", "am", "can", "are", "do", "does"]

        f = open('my_classifier.pickle', 'rb')
        self.classifier = pickle.load(f)
        f.close()

    def is_ques_using_nltk(self, ques):
        """
        This function uses classifier to check whether the message is question or not.
        """
        question_type = self.classifier.classify(
            self.dialogue_act_features(ques))
        return question_type in self.question_types

    def dialogue_act_features(self, post):
        """
        Convert the message to features using tokenizer.
        """
        # TO-DO: Implement TF-IDF based tokenizer for improved accuracy and also train the "my_classifier.pickle" using TF-IDF.
        features = {}
        for word in nltk.word_tokenize(post):
            features['contains({})'.format(word.lower())] = True
        return features

    def is_question(self, question):
        """
        This function checks whether the message passed is question or not. Apart from using "my_classifier.pickle" it uses pattern logic as well as helping verb logic.
        """
        question = str(question).lower().strip()
        if not self.is_ques_using_nltk(question):
            is_ques = False
            # check if any of pattern exist in sentence
            for pattern in self.question_pattern:
                is_ques = pattern in question
                if is_ques:
                    break

            # there could be multiple sentences so divide the sentence
            sentence_arr = question.split(".")
            for sentence in sentence_arr:
                if len(sentence.strip()):
                    # if question ends with ? or start with any helping verb
                    # word_tokenize will strip by default
                    first_word = nltk.word_tokenize(sentence)[0]
                    if sentence.endswith("?") or first_word in self.helping_verbs:
                        is_ques = True
                        break
            return is_ques
        else:
            return True


class Intent:
    """
    class Intent is used to classify the intent of the question i.e whether the question belong to bridging, swapping etc or not.

    """

    def __init__(self, keywords_list):
        self.keywords_list = keywords_list

    def intent(self, x):
        """
        This function classifies the intent using AI21 J1_Jumbo model, by calling their API endpoint with the prompt that we created.

        """
        question = x
        data = requests.post("https://api.ai21.com/studio/v1/j2-light/complete",
                             headers={
                                 "Authorization": "Bearer qdKCmDqcoczLwkMXo37OSBxHEbshjZQq"},
                             json={
                                 "prompt": "question:\n\nHey guys, is it possible to transfer DAI from ethereum mainnet to binance account?\n\nThe intent is: yes \n===\n\nquestion:\n\nHey, I have done withdraw from Polygon -> ETH yesterday and looks like it is stucked. Can someone help me?\n\nThe intent is: yes \n===\nquestion:\n\nHey together, is it possible to swap BNB to Matic?\n\nThe intent is: yes \n===\n\nquestion:\n\nHow is the best way to do?\n\nThe intent is: yes \n===\n\nquestion:\n\nHello, how do I swap ETH to BSC using binance bridge?\n\nThe intent is: yes\n===\nHow can I convert to lunc please?.\n\nThe intent is: yes \n===\n\nquestion:\n\nCan i trade AVAX to USDC?\n\nThe intent is: yes \n===\n\nquestion:\n\nIn Binance can i convert my weth to eth?\n\nThe intent is: yes \n===\n\nquestion:\n\nhow to migrate from old luna to luna2\n\nThe intent is: yes \n===\n\nquestion:\n\nHow to do that\n\nThe intent is: yes \n===\n\nquestion:\n\nHi, is it possible to bridge my ETH from mainnet to Polygon and still keep my ETH on a cold wallet like Trezor?\n\nThe intent is: yes \n===\n\nquestion:\n\nHow to get my 131 usdt in avax c-chain? because of my wrong transaction.\n\nThe intent is: yes\n===\n\nquestion:\n\nWill terra still support luna classic and how?\n\nThe intent is: no\n\n===\n\nquestion:\n\nOk i have question\n\nThe intent is: no\n\n===\n\nquestion:\n\nSo i guess the 26% inflation will fall over time as well as staking rewards?\n\nThe intent is: no\n\n===\n\nquestion:\n\nthank u. so l will have both lunc and luna right?\n\nThe intent is: no\n\n===\n\nquestion:\n\nOkay thanks. That should settle it right ?\n\nThe intent is: no\n\n===\n\nquestion:\n\nit left etherum chain, but doesnt show in avax,  does it take time ?\n\nThe intent is: no\n\n===\n\nquestion:\n\nSo mean same asset only renamed right?\n\nThe intent is: no\n\n===\n\nquestion:\n\ndo i need to add the address\n\nThe intent is: no\n\n===\n\nquestion:\n\nYou can also check by adding the usdc.e address to metamask yes\n\nThe intent is: no\n\n===\n\nquestion:\n\nIve read it but dont really get it, my english is not so good, can you say in simple words for 1000 luna for example do i get 1000 new luna ?\n\nThe intent is: no\n\n===\nquestion:\n\nare there bridges giving out incentives for using them? (excluding Odyssey NFTs)\n\nThe intent is: yes\n\n===\n\nquestion:\n\nCan i bridge from polygon to arbi ?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nthat is i can bridge usdc from polython to arb, for eth?\n\nThe intent is: yes\n\n===\n\nquestion:\n\npolython has weth not eth, can i bridge weth from olython to arb eth?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nWhat is the best bridge (aka lowest fees/most secure) for bridging? Across?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nI need to deposit L1 ETH to Arbitrum L2 ETH instantly. Is there a bridge providing that?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nPossible to bridge from ethereum?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nI'm looking for a way to bridge my eth off of Cronos. Anyone knows how to do this?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nWhere to swap ftm coins?\n\nThe intent is: yes\n\n===\nquestion:\n\nwe have bridge to stargate?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nIs polygon down, i am getting already known error for my transactions even though gas fee is quite high\n\nThe intent is: yes\n\n===\n\nquestion:\n\nHello guys, I can't bridge from optimism to ethereum mainnet using the official bridge, it says \"failed to withdraw\" ?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nhow do you bridge frax/fxs to optimism? cant add the tokens on the official optimism bridge\n\nThe intent is: yes\n\n===\n\nquestion:\n\nI have some matic tokens on etherium block chain how can I move those to polygon chain ?\n\nThe intent is: yes\n===\nquestion:\n\nim having a issue swapp in my pstn to any coin/asset i keep getting this error and no matter what slippage i use it doesnt work any help ?\n\nThe intent is: no\n\n===\n\nquestion:\n\nI have two options, one is UST-GLMR in Stellaswap and the other in Solarflare, how can I know where it was please\n\nThe intent is: no\n\n===\n\nquestion:\n\nhowever, if this was UST, terra collapsed and UST value dropped to nearly 0 so anything in an LP with it would have also dropped\n\nThe intent is: no\n\n===\n\nquestion:\n\nHi, It may take some time for the NFT to appear on Quix. Can you try checking it on Opensea?\n\nThe intent is: no\n\n===\n\nquestion:\n\nSo there are around 1billion tokens circulating?\n\nThe intent is: no\n\n===\n\n\n\nquestion:\n\nHello. I am Laurel from O3 swap. Does anyone know if there's OP builders' group that I can join?\n\nThe intent is: no\n\n===\n\nquestion:\n\nFor example, if you have subnets A, B and C and some composable transaction A -> B -> C, A would be able to know if anything failed on B and C and revert whatever happened on A.\n\nThe intent is: no\n\n===\n\nquestion:\n\nso it will be moved to 0.01% if liquidity increased ?\n\nThe intent is: no\n\n===\n\nquestion:\n\nYeah is was just wondering if theirs some bridge risk such as what happened on harmony\n\nThe intent is: no\n\n===\n\nquestion:\n\nGood to know. Hope it’s fixed soon. New version will make it way a lot smoother to use the web wallet (once the login bug is fixed of course 😅)\n\nThe intent is: no\n\n===\n\nquestion:\n\nHi, i have question\n\nThe intent is: no\n\n===\n\nquestion:\n\nAnd you made everything by the book? Same network, right deposit address, etc\n\nThe intent is: no\n\n===\n\nquestion:\n\nSo you have to pay ETH chain fees when you stake and unstake, right?\n\nThe intent is: no\n===\n\nquestion:\n\nWhat type of tx do I have to look for in the optimist explorer to look for a bridge\n\nThe intent is: no\n\n===\n\nquestion:\n\nyes, but you have to add op token on your matamask first\n\nThe intent is: no\n\n\n\nquestion:\n\nand for that I just need to hold any amount of OP and deligate, correct?\n\nThe intent is: no\n\n===\n\nquestion:\n\ni dunno if they use the same BUID or how this usually works, <@266021304946262017> will be able to help u\n\nThe intent is: no\n\n===\n\nquestion:\n\nand bedrock will be on 12th January yes ?\n\nThe intent is: no\n\n===\n\nquestion:\n\nso 2 k usdc and 2 k husdc?\n\nThe intent is: no\n===\n\nquestion:\n\nhello. is it possible to bridge sol (bsc) to solana?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nHello i was using the polygon bridge to withdraw some token but after hours i dont receive the checkpoint. What is the problem? Is the bridge working?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nHello friends! I'm not able to perform swap on the optimism network with snx, is the network having a problem?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nHello, what is the bridge between luna and luna2?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nHello, is there any way to convert from eth to luna?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nIs there a bridge for eth to luna?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nIs it possible?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nCan u guys help?\n\nThe intent is: yes\n\n===\n\nquestion:\n\nquestion:{question_here}\nThe intent is:".replace(
                                     '{question_here}', question),
                                 "maxTokens": 72,
                                 "temperature": 0.45,
                                 "topKReturn": 0,
                                 "topP": 0.76,
                                 "countPenalty": {
                                     "scale": 0,
                                     "applyToNumbers": False,
                                     "applyToPunctuations": False,
                                     "applyToStopwords": False,
                                     "applyToWhitespaces": False,
                                     "applyToEmojis": False
                                 },
                                 "frequencyPenalty": {
                                     "scale": 0,
                                     "applyToNumbers": False,
                                     "applyToPunctuations": False,
                                     "applyToStopwords": False,
                                     "applyToWhitespaces": False,
                                     "applyToEmojis": False
                                 },
                                 "presencePenalty": {
                                     "scale": 0,
                                     "applyToNumbers": False,
                                     "applyToPunctuations": False,
                                     "applyToStopwords": False,
                                     "applyToWhitespaces": False,
                                     "applyToEmojis": False
                                 },
                                 "stopSequences": ["==="]
                             }
                             )
        return data.json()['completions'][0]['data']['text']

    def get_narrow_filter(self, x):
        """
        This function applies narrow filter to the question i.e we check if the certain keywords are present in the question we mark that question as potentially
        valuable question.
        """
        # filters = ['swap', 'bridge', 'cross chain bridge',
        #            'cross chain', 'mutlichain']  # keyword list
        filters = self.keywords_list
        for i in filters:
            if i in x:
                return 'yes'
        return 'no'


class DataBase:
    """
    Class for MongoDB database initialisation
    """

    def __init__(self):
        """
        Constructor for Database class, takes general MongoClient URI and MongoDB database name.
        """
        self.client = pymongo.MongoClient(
            "mongodb+srv://chirayuu:bitbaza000@slack.ok4sm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db = self.client["social_listener"]

    # def get_collection(self,name):
    #     return self.db[name]

    def insert(self, df, name):
        """
        This function inserts the whole passed DataFrame to mongoDB.
        """
        json = df.to_dict('records')
        col = self.db[name]  # name is the name of collection.
        col.insert_many(json)
        self.client.close()

    # def insert_one(self,dic,name='test'):
    #     json = dic
    #     col = self.db[name]
    #     col.insert_many(json)
    #     self.client.close()

    # def getone(self):
    #     col = self.db['test']
    #     x = list(col.find().sort('_id',pymongo.DESCENDING).limit(1))
    #     print(x)

# dic = [{"is_relevant":None}]
# d = DataBase()
# d.getone()
# d.insert_one(dic)
# c = Classifier()
# print(c.is_question("Is there any admin can help me!i use bridge from matic network to eth network,but Havent been successful"))

# s = Scrape()
# df = s.scrape_discord()
# print(df)

# i =  Intent()
# print(i.intent("Is there any admin can help me!i use bridge from matic network to eth network,but Havent been successful"))
