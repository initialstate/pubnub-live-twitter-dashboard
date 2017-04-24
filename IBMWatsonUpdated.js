// require xhr
const XHR = require('xhr');

// require state
const db = require('kvstore');
const qs = require('codec/query_string');

export default (request) => {
    
    // api credentials
    const apiUsername = 'IBM_API_Username';
    const apiPW = 'IBM_API_Password';
    
    const apiVersion = '2017-02-27'
    
    // url for sentiment analysis api
    const apiUrl = 'https://'+apiUsername+':'+apiPW+'@gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze';
    
    const querystring = qs.stringify({
        version: apiVersion,
        text: request.message.text,
        features: 'sentiment',
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
            const type = body.sentiment.document.label;
            const score = body.sentiment.document.score;
            const cur = sessionSentiment[type] || { count: 0, avg: 0 };
            const curSum = cur.avg * cur.count;
            const newtotal = ++(cur.count);
            const newAvg = ((curSum) + Number(score)) / newtotal;
            console.log(newAvg);
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
            request.message.body = body;
            request.message.score = score;
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
    };
