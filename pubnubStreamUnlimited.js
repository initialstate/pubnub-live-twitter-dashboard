var PubNub = require('pubnub')

var Twitter = require('twitter');

// Variables that contains the user credentials to access Twitter API
var client = new Twitter({
	consumer_key: 'Twitter_Consumer_Key',
	consumer_secret: 'Twitter_Consumer_Secret',
	access_token_key: 'Twitter_Access_Token',
	access_token_secret: 'Twitter_Access_Token_Secret'
});

// Configure personal subscribe and publish key
var pubnubPersonal = new PubNub({
	publishKey: "Pubnub_Publish_Key",
	subscribeKey: "Pubnub_Subscribe_Key",
})

// Initiate session_id for the Watson block
var session_Id = 0;

// Receive tweets from the Twitter stream based on keywords below 
var stream = client.stream('statuses/filter', {track: 'Trump,trump,POTUS,potus,Potus'});

stream.on('data', function(event) {
	session_Id++;
	// Where we publish tweets for sentiment analysis
	var publishConfig = {
		channel : "sentiment-analysis",
		message : {"session_id":session_Id,"text":event.text}
	}
	pubnubPersonal.publish(publishConfig, function(status, response) {
		if (status.error) {
			console.log(status, response);
		}
	})
});
 
stream.on('error', function(error) {
	console.log(error);
});

// Listener on our PubNub app channel
pubnubPersonal.addListener({
	
	message: function(m) {
		// Your Initial State bucket key
		// Make sure to create a bucket in IS with the same key
		var bucketKey = "pubnubtrump"
		var msg = m.message;

		// Here we construct and publish a payload made up of parameters from sentiment analysis
		if ("session_sentiment" in msg) {
			var payloadMsg = {"key": "Tweet","value": msg.text}
			console.log(msg.text);

			if ("positive" in msg.session_sentiment) {
				payloadPos = {"key": "Positive Level","value":msg.session_sentiment.positive.count}
			} else {
				payloadPos = {"key": "Positive Level","value":0}
			};
			if ("negative" in msg.session_sentiment) {
				payloadNeg = {"key": "Negative Level","value":msg.session_sentiment.negative.count}
			} else {
				payloadNeg = {"key": "Negative Level","value":0}
			};
			if ("neutral" in msg.session_sentiment) {
				payloadNeut = {"key": "Neutral Level","value":msg.session_sentiment.neutral.count}
			} else {
				payloadNeut = {"key": "Neutral Level","value":0}
			};

			payloadScore = {"key": "Score","value": msg.score}

			var publishConfig = {
				channel : "initial-state-streamer",
				message : {"events": [payloadMsg,payloadPos, payloadNeg, payloadNeut, payloadScore],"bucketKey":bucketKey}
			}
			pubnubPersonal.publish(publishConfig, function(status, response) {
				if (status.error) {
					console.log(status, response);
				}
			})
		} else {
			console.log("No sentiment message from Watson");
		}
	}
	
})


// Configure PubNub subscriptions

pubnubPersonal.subscribe({
	channels: ['sentiment-analysis'],
})
