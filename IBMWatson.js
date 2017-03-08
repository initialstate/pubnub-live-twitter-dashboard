// require xhr
const XHR = require('xhr');

// require state
const db = require('kvstore');
const qs = require('codec/query_string');

export default (request) => {
    // url for sentiment analysis api
    const apiUrl = 'https://gateway-a.watsonplatform.net/calls/text/TextGetTextSentiment';

    // api key
    const apiKey = 'Your_API_Key';



    const querystring = qs.stringify({
        outputMode: 'json',
        showSourceText: false,
        text: request.message.text,
        apikey: apiKey
    });
    const sessionId = request.message.session_id;

    return db.get('sentiment_db').then(function (val) {
        const sentimentDb = val || {};
        const sessionSentiment = sentimentDb[sessionId] || {
            overall: 0,
            positive: {
                count: 0,
                avg: 0
            },
            negative: {
                count: 0,
                avg: 0
            }
        };

        return XHR.fetch(apiUrl + '?' + querystring).then(function (r) {
            console.log(r);
            const body = JSON.parse(r.body);
            const type = body.docSentiment.type;
            const score = body.docSentiment.score;
            const cur = sessionSentiment[type] || { count: 0, avg: 0 };
            const curSum = cur.avg * cur.count;
            const newtotal = ++(cur.count);
            const newAvg = ((curSum) + Number(score)) / newtotal;

            sessionSentiment[type] = {
                count: newtotal,
                avg: newAvg
            };

            sessionSentiment.overall =
                (sessionSentiment.positive.count
                    * sessionSentiment.positive.avg) +
                (sessionSentiment.negative.count
                    * sessionSentiment.negative.avg);

            sentimentDb[sessionId] = sessionSentiment;

            db.set('sentiment_db', sentimentDb);

            request.message.session_id = sessionId;
            request.message.session_sentiment = sessionSentiment;
            request.message.score =
                sessionSentiment.overall + (Math.random() / 10000);

            return request.ok();
        })
        .catch(function (e){
            console.error(e);
            return request.ok();
        });
    });
}
