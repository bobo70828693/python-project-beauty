import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random

def initFirebase():
    # 引用私密金鑰
    cred = credentials.Certificate('./serviceAccount.json')

    # init firebase
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://python-project-beauty.firebaseio.com/"
    })

    return 'ok'

def addFirebase(data):
    print(data['title'])
    ref = db.reference('beauty/')
    postRef = ref.push()
    postRef.set(data)

    return 'ok'

def getFirebaseData():
    ref = db.reference('beauty/')
    data = ref.get()

    return data
