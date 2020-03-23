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
