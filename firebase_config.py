import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://emergency-contacts-app-default-rtdb.firebaseio.com/'
})

contacts_ref = db.reference("/contacts")
