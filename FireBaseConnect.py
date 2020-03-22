import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random

def initFirebase():
    # 引用私密金鑰
    cred = credentials.Certificate('./serviceAccount.json')

    # init firebase
    firebase_admin.initialize_app(cred)

    # init firestore
    firebase = firestore.client()

    return firebase

def addFirebase(firebaseHandle, title, data):
    docRef = firebaseHandle.collection("beauty").document(title)

    docRef.set(data)

    return 'ok'

def getFirebaseData(firebaseHandle):
    path = 'beauty'
    docs = firebaseHandle.collection(path).get()

    return docs

# firebase = initFirebase()
# retrieveData = getFirebaseData(firebase)
# totalData = []
# for data in retrieveData:
#     formatData = data.to_dict()
#     formatData['title'] = data.id
#     totalData += [formatData]
# rndData = random.choice(totalData)
# imgUrl = random.choice(rndData['images'])

# sendText = rndData['title'] + "\n"
# if rndData['fbLink'] != '':
#     sendText += "facebook: " + rndData['fbLink'] + "\n"

# if rndData['insLink'] != '':
#     sendText += "instagram: " + rndData['insLink'] + "\n"

# sendText += imgUrl
