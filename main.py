from flask import Flask, request, Response
import json
import slack
import FireBaseConnect
import random
import time

app = Flask(__name__)
FireBaseConnect.initFirebase()
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def getWebHook():
    client = slack.WebClient("xoxb-10539333943-1016858910580-CFm3T6PGc0jk9j2TM5xTnnpa")
    requestData = request.get_json()
    time.sleep(1.5)
    if requestData['type'] == "url_verification":
        return json.dumps(requestData['challenge'])

    if 'event' in requestData:
        if 'text' in requestData['event']:
            if requestData['event']['text'] == "桑":
                retrieveData = FireBaseConnect.getFirebaseData()
                totalData = []
                for hashid, data in retrieveData.items():
                    data['key'] = hashid
                    totalData += [data]
                rndData = random.choice(totalData)
                imgUrl = random.choice(rndData['images'])

                sendText = rndData['title'] + rndData['key'] + "\n"
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