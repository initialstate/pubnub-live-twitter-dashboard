from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from geolocation.main import GoogleMaps
from time import sleep

google_maps = GoogleMaps(api_key='Your_Google_API_Key') 

# Configure Twitter subscribe key
pnconfigTwitter = PNConfiguration()
 
pnconfigTwitter.subscribe_key = 'sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe'

pubnubTwitter = PubNub(pnconfigTwitter)

# Configure personal subscribe and publish key
pnconfigPersonal = PNConfiguration()

pnconfigPersonal.subscribe_key = 'Your_PubNub_App_Subscribe_Key'
pnconfigPersonal.publish_key = 'Your_PubNub_App_Publish_Key'

pubnubPersonal = PubNub(pnconfigPersonal)


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


# Callback for twitter channel
class TwitterSubscribeCallback(SubscribeCallback):

    # We are filtering tweets based on these words
    keywords = ['Trump','trump','POTUS','potus']
    # Initiate session_id for the Watson block
    session_Id = 0

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

    # Where we filter tweets and publish for sentiment analysis
    def message(self, pubnub, message):
        if any(i in message.message['text'] for i in self.keywords):
            sleep(90)
            self.session_Id = self.session_Id + 1
            try:
                location = google_maps.search(location=message.message['place']['full_name'])
                my_location = location.first()
                TwitterSubscribeCallback.coord = str(my_location.lat) + "," + str(my_location.lng)
                pass
            except AttributeError:
                TwitterSubscribeCallback.coord = "none"
                pass

            pubnubPersonal.publish().channel("sentiment-analysis").message({"session_id":self.session_Id,"text":message.message['text']}).async(my_publish_callback)
        else:
            pass
            

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

                if message.message['score'] > 0.25:
                    payloadCoord={"key": "User Location Pos","value":TwitterSubscribeCallback.coord}
                elif message.message['score'] < -0.25:
                    payloadCoord={"key": "User Location Neg","value":TwitterSubscribeCallback.coord}
                elif TwitterSubscribeCallback.coord == "none":
                    payloadCoord={"key": "User Location","value":"No location data"}
                else:
                    payloadCoord={"key": "User Location Neut","value":TwitterSubscribeCallback.coord}
                
                payload=merge(payloadMsg,payloadPos,payloadNeg,payloadNeut,payloadScore,payloadCoord)
                
                print payload
                payload = {"events": payload, "bucketKey": self.bucket_key}

                pubnubPersonal.publish().channel("initial-state-streamer").message(payload).async(my_publish_callback)
                
                previous_message = message.message
                pass
            else:
                print "No sentiment message from Watson"
                pass
        else:
            print "Duplicate Message"
            pass


# Function that batches all the events associated with one tweet
def merge(set1,set2,set3,set4,set5,set6):
    lst=[]
    lst.append(set1)
    lst.append(set2)
    lst.append(set3)
    lst.append(set4)
    lst.append(set5)
    lst.append(set6)
    return lst



# Configure PubNub subscriptions

pubnubTwitter.add_listener(TwitterSubscribeCallback())
pubnubTwitter.subscribe().channels('pubnub-twitter').execute()

pubnubPersonal.add_listener(SentimentSubscribeCallback())
pubnubPersonal.subscribe().channels('sentiment-analysis').execute()
