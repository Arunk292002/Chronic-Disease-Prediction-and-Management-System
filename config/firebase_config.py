import pyrebase

firebaseConfig = {"Add Firebase Configurations"}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
