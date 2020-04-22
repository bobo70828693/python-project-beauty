from flask import Flask, request, Response, make_response
import json
import slack
from slack.errors import SlackApiError
import FireBaseConnect
import random
import os
import hashlib
import re
import time
import CrawlerBeauty
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def getWebHook():
    slackApiToken = os.getenv('SLACK_API_TOKEN')
    slackUserApiToken = os.getenv('SLACKE_USER_API_TOKEN')
    userClient = slack.WebClient(token=slackUserApiToken, ssl=True)
    client = slack.WebClient(token=slackApiToken, ssl=True)
    requestData = request.get_json()
    if requestData['type'] == "url_verification":
        return json.dumps(requestData['challenge'])

    if 'event' in requestData:
        if 'type' in requestData['event']:
            if requestData['event']['type'] == "message":
                if 'text' in requestData['event']:
                    userInfo = userClient.users_info(user=requestData['event']['user'])
                    if request.headers.get('X-Slack-Retry-Reason', 0) == 0:
                        if userInfo['user']['profile']['display_name'] != 'Hoq':
                            if requestData['event']['text'] == "桑":
                                app.logger.info("Request Body: " + request.get_data(as_text=True))
                                sendMessage(client, 'beauty', requestData['event']['channel'])
                                return make_response("OK", 200)
                            elif requestData['event']['text'] == '爆桑':
                                sendMessage(client, 'beautyPlus', requestData['event']['channel'])
                                return make_response("OK", 200)
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
                                    for key in range(len(userLikeList)):
                                        if key == 5:
                                            break
                                        else:
                                            sendText = random.choice(userLikeList)
                                            client.api_call("chat.postMessage", json={"channel":requestData['event']['channel'], "text": sendText})
                        else:
                            terribleData = FireBaseConnect.getFirebaseData('terrible')
                            rndTerrible = random.choice(terribleData)
                            sendText = "給你滿滿的大恬娃，恬娃愛你喔<3\n" + rndTerrible
                            client.api_call("chat.postMessage", json={"channel":requestData['event']['channel'], "text": sendText})
                    return make_response("OK", 200, {"X-Slack-No-Retry": 1, "content_type": "application/json"})
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
                    

    return make_response("OK", 200, {"X-Slack-No-Retry": 1})

@app.route("/crawlerBeauty", methods=['GET'])
def crawlerBeauty():
    CrawlerBeauty.CrawlerData()

def sendMessage(client, path, channel):
    retrieveData = FireBaseConnect.getFirebaseData(path)
    totalData = []
    for hashid, data in retrieveData.items():
        totalData += [{
                'fbLink': data.get('fbLink', ''), 
                'insLink': data.get('insLink', ''), 
                'hashid': hashid, 
                'images': data.get('images', ''),
                'title': data.get('title', '')}]

    rndData = random.choice(totalData)
    loop = 0
    sendText = rndData.get('title', '') + "\n" if rndData.get('title', '') != '' else ''
    sendText += "facebook: " + rndData.get('fbLink', '') + "\n" if rndData.get('fbLink', '') != '' else ''
    sendText += "instagram: " + rndData.get('insLink', '') + "\n" if rndData.get('insLink', '') != '' else ''
    imgLen = len(rndData['images'])
    for imgUrl in rndData.get('images', []): 
        if imgLen < 5:
            sendText += imgUrl
        else:
            sendText += random.choice(rndData['images'])
        
        if loop == 5:
            break
        
        response = client.api_call("chat.postMessage", json={"channel":channel, "text": sendText})
        sendText = ''
        loop+=1
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)