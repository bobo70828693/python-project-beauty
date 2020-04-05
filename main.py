from flask import Flask, request, Response
import json
import slack
import FireBaseConnect
import random
import os
import hashlib
import re
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def getWebHook():
    slackApiToken = os.getenv('SLACK_API_TOKEN')
    client = slack.WebClient(slackApiToken)
    requestData = request.get_json()
    app.logger.info("Request Body: " + request.get_data(as_text=True))
    if requestData['type'] == "url_verification":
        return json.dumps(requestData['challenge'])

    if 'event' in requestData:
        if 'type' in requestData['event']:
            if requestData['event']['type'] == "message":
                if 'text' in requestData['event']:
                    if requestData['event']['text'] == "桑":
                        retrieveData = FireBaseConnect.getFirebaseData('beauty/')
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
                    elif requestData['event']['text'] == '我桑':
                        userId = requestData['event']['user']
                        s = hashlib.sha1()
                        s.update(userId.encode('utf-8'))
                        enUserId = s.hexdigest()
                        path = 'users/{userId}/'.format(userId=enUserId)

                        userLikeList = FireBaseConnect.getFirebaseData(path)
                        if not userLikeList:
                            sendText = "沒東西桑個毛"
                        else:
                            sendText = random.choice(userLikeList)

                        client.chat_postMessage(channel=requestData['event']['channel'], text=sendText)
            elif requestData['event']['type'] == "reaction_added":
                if requestData['event']['reaction'] == 'heart':
                    userId = requestData['event']['user']
                    s = hashlib.sha1()
                    s.update(userId.encode('utf-8'))
                    enUserId = s.hexdigest()
                    path = 'users/' + enUserId + '/'

                    reactionMsg = client.reactions_get(channel=requestData['event']['item']['channel'], timestamp=requestData['event']['item']['ts'])

                    pattern = re.compile('https://i.imgur.com/[^>]*')
                    result = re.search(pattern, reactionMsg['message']['text'])
                    imgUrl = result.group(0)

                    userLikeList = FireBaseConnect.getFirebaseData(path)
                    # not (userLikeList is none)
                    if not userLikeList:
                        # None
                        userLikeList = []
                        userLikeList += [imgUrl]
                    else:
                        # not None
                        if imgUrl not in userLikeList:
                            userLikeList += [imgUrl]

                    FireBaseConnect.insertData(path, userLikeList)
            elif requestData['event']['type'] == 'reaction_removed':
                if requestData['event']['reaction'] == 'heart':
                    userId = requestData['event']['user']
                    s = hashlib.sha1()
                    s.update(userId.encode('utf-8'))
                    enUserId = s.hexdigest()
                    path = 'users/' + enUserId + '/'

                    reactionMsg = client.reactions_get(channel=requestData['event']['item']['channel'], timestamp=requestData['event']['item']['ts'])

                    pattern = re.compile('https://i.imgur.com/[^>]*')
                    result = re.search(pattern, reactionMsg['message']['text'])
                    imgUrl = result.group(0)

                    userLikeList = FireBaseConnect.getFirebaseData(path)
                    # not (userLikeList is none)
                    if userLikeList:
                        # not None
                        if imgUrl in userLikeList:
                            userLikeList.remove(imgUrl)
                            FireBaseConnect.insertData(path, userLikeList)
                    

    return json.dumps('ok')
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)