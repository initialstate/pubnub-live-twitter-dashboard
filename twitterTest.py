from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# Configure Twitter subscribe key
pnconfigTwitter = PNConfiguration()
 
pnconfigTwitter.subscribe_key = 'sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe'

pubnubTwitter = PubNub(pnconfigTwitter)



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
            print message.message['text']
        else:
            pass


# Configure PubNub subscriptions

pubnubTwitter.add_listener(TwitterSubscribeCallback())
pubnubTwitter.subscribe().channels('pubnub-twitter').execute()
