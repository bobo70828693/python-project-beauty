import FireBaseConnect
import requests
import re
import time
from time import strftime, strptime
from datetime import datetime
from bs4 import BeautifulSoup

def CrawlerData():
    request = requests.session()
    payLoad = {
        "form": "/bbs/Beauty/index.html",
        "yes": "yes"
    }
    request.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.htmld",payLoad)

    domain = "https://www.ptt.cc"
    url = "https://www.ptt.cc/bbs/Beauty/index.html"
    requestText = request.get(url)

    startPoint = 0
    startFlag = 1
    exitFlag = 0
    while exitFlag == 0:
        soup = BeautifulSoup(requestText.text, 'html.parser')

        #取得上頁URL
        nextPage = soup.find_all("a", string="‹ 上頁")
        nextPageUrl = ''
        if nextPage == None:
            exitFlag = 1
        else:
            nextPageUrl = min(nextPage)['href']
        print(nextPageUrl)

        # check last page
        numRe = re.search("index\d{4}", nextPageUrl)
        numStr = numRe.group(0)[5:9]

        lastPageNum = FireBaseConnect.getFirebaseData('page')
        if lastPageNum != None:
            if startFlag == 1:
                startPoint = int(numStr) + 1
                startFlag = 0

            if (lastPageNum - 1) == int(numStr):
                exitFlag = 1

        # 整理取得資料
        hrefList = soup.select('div.title a')
        for oneHref in hrefList:
            imageList = []
            instagram = ""
            facebook = ""
            if oneHref.text[0:4] == "[正妹]":
                innerInfo = request.get(domain + oneHref['href'])
                beautyInfo = BeautifulSoup(innerInfo.text, 'html.parser')
                pushTag = beautyInfo.find_all("span", class_="push-tag", string="推 ")
                createdAt = beautyInfo.select('span.article-meta-value')[-1].get_text()
                if len(createdAt) == 24:
                    datetimeObj = datetime.strptime(createdAt, "%a %b %d %H:%M:%S %Y")
                    instagramLink = beautyInfo.find("a", string=re.compile("(instagram)"))
                    facebookLink = beautyInfo.find("a", string=re.compile("(facebook)"))
                    if instagramLink != None:
                        instagram = instagramLink['href']
                    if facebookLink != None:
                        facebook = facebookLink['href']

                    images = beautyInfo.find_all("a", string=re.compile("^https://i.imgur.com/"))
                    for image in images:
                        imageList += [image.text]
                    
                    if len(pushTag) >= 90:
                        path = 'beautyPlus'
                    else:
                        path = 'beauty'

                    # 字串處理
                    title = re.sub("[^\u4E00-\u9FFF]", "", oneHref.text.replace("[正妹] ", ""))
                    print(title, len(pushTag))
                    if len(imageList) != 0 and title != "" and (title.find("大尺碼") == -1):
                        data = {
                            "title": title,
                            "images": imageList,
                            "insLink": instagram,
                            "fbLink": facebook,
                            "created_at": datetimeObj.strftime("%Y-%m-%d %H:%M:%S")
                        }

                        FireBaseConnect.addFirebase(path, data)
        if nextPageUrl != '':
            requestText = request.get(domain + nextPageUrl)
    FireBaseConnect.insertData('page', startPoint)