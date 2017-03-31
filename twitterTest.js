var PubNub = require('pubnub')

// Configure Twitter subscribe key
var pubnubTwitter = new PubNub({
    subscribeKey: "sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe",
})

// Listener on the Twitter channel
pubnubTwitter.addListener({

    message: function(m) {

        var msg = m.message;

		// We are filtering tweets based on Trump, trump, or any capitilization of POTUS
        if (msg.text.match(/([T|t]rump|[P|p][O|o][T|t][U|u][S|s])/g)) {
        	console.log(msg.text);
        }
    }
})

// Configure PubNub subscriptions

pubnubTwitter.subscribe({
    channels: ['pubnub-twitter'],
})
