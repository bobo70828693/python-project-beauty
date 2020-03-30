from flask import Flask, request, Response
import json
import slack
import FireBaseConnect
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
FireBaseConnect.initFirebase()
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def getWebHook():
    slackApiToken = os.getenv('SLACK_API_TOKEN')
    client = slack.WebClient(slackApiToken)
    requestData = request.get_json()
    if requestData['type'] == "url_verification":
        return json.dumps(requestData['challenge'])

    if 'event' in requestData:
        if 'text' in requestData['event']:
            if requestData['event']['text'] == "桑":
                retrieveData = FireBaseConnect.getFirebaseData()
                totalData = []
                for hashid, data in retrieveData.items():
                    fbLink = ''
                    insLink = ''
                    images = []
                    title = ''
                    if 'fbLink' in data:
                        fbLink = data['fbLink']

                    if 'insLink' in data:
                        insLink = data['insLink']
                    
                    if 'images' in data:
                        images = data['images']
                    
                    if 'title' in data:
                        title = data['title']


                    totalData += [
                        {
                            "fbLink": fbLink,
                            "insLink": insLink,
                            "images": images,
                            "title": title,
                            "hashid": hashid
                        }
                    ]
                rndData = random.choice(totalData)
                imgUrl = random.choice(rndData['images'])

                sendText = rndData['title'] + rndData['hashid'] + "\n"
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