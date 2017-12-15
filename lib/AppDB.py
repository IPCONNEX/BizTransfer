from pymongo import MongoClient
import os


class AppDB:
    def __init__(self, uri, user, pwd, name):
        client = MongoClient(uri)
        DB = client.get_database(name)
        DB.authenticate(user, pwd)
        self.collections = DB

    def GetUsersDB(self):
        return self.collections.users

    def GetEnterprisesDB(self):
        return self.collections.enterprises

    def GetLanguageStatics(self, language):
        return self.collections.statics.find_one({'language': language}, {'_id': False})

    def GetDictionaries(self):
        return self.collections.statics


#  TODO complete full profile data fields
class Profile:
    def __init__(self):
        self.summary = {'post_id': '', 'business_title': ''}
        self.ask_price = ''

class EmailAccount:
    server = os.environ.get('EMAIL_SERVER')


#  TODO class enterprise to structure DB data