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

def addFirebase(path, data):
    ref = db.reference(path)
    postRef = ref.push()
    postRef.set(data)

    return 'ok'

def insertData(path, data):
    ref = db.reference(path)
    ref.set(data)

    return 'ok'

def getFirebaseData(path):
    ref = db.reference(path)
    data = ref.get()

    return data

def deleteFirebaseData():
    ref = db.reference('beauty/')
    ref.delete()


initFirebase()