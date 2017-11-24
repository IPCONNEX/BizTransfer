from pymongo import MongoClient


class AppDB():
    def __init__(self):
        #  TODO get the credential from a local file
        uri = 'mongodb://ds243055.mlab.com:43055'
        user = 'mac'
        pwd = 'mac'
        client = MongoClient(uri)
        DB = client.biztransfer
        DB.authenticate(user, pwd)
        self.collection = DB

    def GetUsersDB(self):
        return self.collection.users

    def GetEnterprisesDB(self):
        return self.collection.enterprises

    def GetLanguageStatics(self, language):
        return self.collection.statics.find_one({'language':language}, {'_id': False})


#  TODO complete full profile data fields
class Profile():
    def __init__(self):
        self.summary = {'post_id': '', 'business_title': ''}
        self.ask_price = ''

