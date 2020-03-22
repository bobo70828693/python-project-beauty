import FireBaseConnect
import requests
import re
from bs4 import BeautifulSoup

request = requests.session()
payLoad = {
    "form": "/bbs/Beauty/index.html",
    "yes": "yes"
}
request.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.htmld",payLoad)

domain = "https://www.ptt.cc"
url = "https://www.ptt.cc/bbs/Beauty/index.html"
requestText = request.get(url)

# init firebae
firebase = FireBaseConnect.initFirebase()

exitFlag = 0
while exitFlag == 0:
# for page in range(2):
    soup = BeautifulSoup(requestText.text, 'html.parser')

    #取得上頁URL
    nextPage = soup.find_all("a", string="‹ 上頁")
    nextPageUrl = ''
    if nextPage == None:
        exitFlag = 1
    else:
        nextPageUrl = min(nextPage)['href']
    print(nextPageUrl)

    # 整理取得資料
    hrefList = soup.select('div.title a')
    for oneHref in hrefList:
        imageList = []
        instagram = ""
        facebook = ""
        if oneHref.text[0:4] == "[正妹]":
            print(oneHref.text)
            innerInfo = request.get(domain + oneHref['href'])
            beautyInfo = BeautifulSoup(innerInfo.text, 'html.parser')
            instagramLink = beautyInfo.find("a", string=re.compile("(instagram)"))
            facebookLink = beautyInfo.find("a", string=re.compile("(facebook)"))
            if instagramLink != None:
                instagram = instagramLink['href']
            if facebookLink != None:
                facebook = facebookLink['href']

            images = beautyInfo.find_all("a", string=re.compile("^https://i.imgur.com/"))
            for image in images:
                imageList += [image.text]
            
            data = {
                "images": imageList,
                "insLink": instagram,
                "fbLink": facebook
            }

            FireBaseConnect.addFirebase(firebase, oneHref.text, data)
    if nextPageUrl != '':
        requestText = request.get(domain + nextPageUrl)