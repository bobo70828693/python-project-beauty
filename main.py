from flask import Flask, request, Response
import json
import slack
import FireBaseConnect
import random

app = Flask(__name__)
firebase = FireBaseConnect.initFirebase()
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def getWebHook():
    client = slack.WebClient("xoxb-10539333943-1016858910580-kGCKA1eoZC5VgLN8kO2srtlT")
    requestData = request.get_json()

    if requestData['type'] == "url_verification":
        return json.dumps(requestData['challenge'])

    if 'event' in requestData:
        if requestData['event']['text'] == "桑":
            retrieveData = FireBaseConnect.getFirebaseData(firebase)
            totalData = []
            for data in retrieveData:
                formatData = data.to_dict()
                formatData['title'] = data.id
                totalData += [formatData]
            rndData = random.choice(totalData)
            imgUrl = random.choice(rndData['images'])
            
            sendText = rndData['title'] + "\n"
            if rndData['fbLink'] != '':
                sendText += "facebook: " + rndData['fbLink'] + "\n"

            if rndData['insLink'] != '':
                sendText += "instagram: " + rndData['insLink'] + "\n"

            sendText += imgUrl
            
            client.chat_postMessage(channel=requestData['event']['channel'], text=sendText)
            return json.dumps('ok')
    return json.dumps('ok')
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)