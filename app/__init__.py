import os

# ---------- Uncomment below if you wish to start chatbot backend in localhost
# from app.model.secret_idandkeys import SecretData as s
# os.environ["GOOGLE_CREDENTIALS"] = s.getSecrets('GOOGLE_CREDENTIALS') # contents of json key
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = s.getSecrets('GOOGLE_APPLICATION_CREDENTIALS') # json key for google project link to dialogflow
# os.environ['PROJECT_ID'] = s.getSecrets('PROJECT_ID')# google project id
# os.environ['TELEGRAM_TOKEN'] = s.getSecrets('TELEGRAM_TOKEN') # token for telegram bot
# ----------

here = os.path.dirname(os.path.abspath(__file__))
jsonkey = open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], "w")
# print(repr(os.environ["GOOGLE_CREDENTIALS"]))
jsonkey.write(repr(os.environ["GOOGLE_CREDENTIALS"].replace("\\n", "\n"))[1:-1])
jsonkey.close()




