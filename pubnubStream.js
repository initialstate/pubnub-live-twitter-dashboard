var PubNub = require('pubnub')

// Configure Twitter subscribe key
var pubnubTwitter = new PubNub({
	subscribeKey: "sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe",
})

// Configure personal subscribe and publish key
var pubnubPersonal = new PubNub({
	publishKey: "PubNub Publish Key",
	subscribeKey: "PubNub Suscribe Key",
})

// Initiate session_id for the Watson block
var session_Id = 0;

// Listener on the Twitter channel
pubnubTwitter.addListener({

	message: function(m) {

		var msg = m.message;

		// We are filtering tweets based on Trump, trump, or any capitilization of POTUS
		if (msg.text.match(/([T|t]rump|[P|p][O|o][T|t][U|u][S|s])/g)) {
			session_Id++;
			// Where we publish tweets for sentiment analysis
			var publishConfig = {
				channel : "sentiment-analysis",
				message : {"session_id":session_Id,"text":msg.text}
			}
			pubnubPersonal.publish(publishConfig, function(status, response) {
				if (status.error) {
					console.log(status, response);
				}
			})
		}
	}

})

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

pubnubTwitter.subscribe({
	channels: ['pubnub-twitter'],
})

pubnubPersonal.subscribe({
	channels: ['sentiment-analysis'],
})
