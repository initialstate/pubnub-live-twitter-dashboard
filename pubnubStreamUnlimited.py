from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

# Variables that contains the user credentials to access Twitter API 
access_token = "Twitter_Access_Token"
access_token_secret = "Twitter_Access_Token_Secret"
consumer_key = "Twitter_Consumer_Key"
consumer_secret = "Twitter_Consumer_Secret"

# Configure personal subscribe and publish key
pnconfigRachel = PNConfiguration()

pnconfigRachel.subscribe_key = 'Pubnub_Subscribe_Key'
pnconfigRachel.publish_key = 'Pubnub_Publish_Key'

pubnubRachel = PubNub(pnconfigRachel)


# Callback for any publish
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        print("Published")
        pass  # Message successfully published to specified channel.
    else:
        print("Publish Error")
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    # Initiate session_id for the Watson block
    session_Id = 0

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            self.session_Id = self.session_Id + 1
            pubnubRachel.publish().channel("sentiment-analysis").message({"session_id":self.session_Id,"text":tweet['text']}).async(my_publish_callback)
            return True
        except KeyError:
            pass

    def on_error(self, status):
        print status
            

# Callback for sentiment channel        
class SentimentSubscribeCallback(SubscribeCallback):
    # Your Initial State bucket key
    # Make sure to create a bucket in IS with the same key
    bucket_key = "pubnubtrump"

    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost
        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
    
    # Here we construct and publish a payload made up of parameters from sentiment analysis
    def message(self, pubnub, message):
        previous_message = "placeholder"
        if previous_message != message.message:
            if 'session_sentiment' in message.message:
                payloadMsg = {"key": "Tweet","value": message.message['text']}
                if 'positive' in message.message['session_sentiment']:
                    payloadPos = {"key": "Positive Level","value":message.message['session_sentiment']['positive']['count']}
                else:
                    payloadPos = {"key": "Positive Level","value":0}
                if 'negative' in message.message['session_sentiment']:
                    payloadNeg={"key": "Negative Level","value": message.message['session_sentiment']['negative']['count']}
                else:
                    payloadNeg={"key": "Negative Level","value": 0}
                if 'neutral' in message.message['session_sentiment']:
                    payloadNeut={"key": "Neutral Level","value": message.message['session_sentiment']['neutral']['count']}
                else:
                    payloadNeut={"key": "Neutral Level","value": 0}

                payloadScore={"key": "Score","value": message.message['score']}
                
                payload=merge(payloadMsg,payloadPos,payloadNeg,payloadNeut,payloadScore)
                
                print payload
                payload = {"events": payload, "bucketKey": self.bucket_key}

                pubnubRachel.publish().channel("initial-state-streamer").message(payload).async(my_publish_callback)
                
                previous_message = message.message
                pass
            else:
                print "No sentiment message from Watson"
                pass
        else:
            print "Duplicate Message"
            pass


# Function that batches all the events associated with one tweet
def merge(set1,set2,set3,set4,set5):
    lst=[]
    lst.append(set1)
    lst.append(set2)
    lst.append(set3)
    lst.append(set4)
    lst.append(set5)
    return lst


# Configure PubNub subscriptions
pubnubRachel.add_listener(SentimentSubscribeCallback())
pubnubRachel.subscribe().channels('sentiment-analysis').execute()

#This handles Twitter authetification and the connection to Twitter Streaming API
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)

#This line filters Twitter Streams to capture data by the keywords below
stream.filter(track=['Trump','trump','POTUS','potus'])
