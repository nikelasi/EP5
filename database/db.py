import os, pymongo
from .collections import prefixes, users, items, message_info

class Database:
	"""Class to handle the whole database"""
	def __init__(self, password, dbname, username, clustername):
		self.password = password
		self.dbname = dbname
		self.username = username
		self.clustername = clustername
		self.cluster = pymongo.MongoClient(f"mongodb+srv://{self.username}:{self.password}@{self.clustername}.jhxcv.mongodb.net/{self.dbname}?retryWrites=true&w=majority")
		self.database = self.cluster[self.dbname]

		self.prefix_db = prefixes.Database(self.database)
		self.user_db = users.Database(self.database, self)
		self.items_db = items.Database(self.database, self)
		self.message_info_db = message_info.Database(self.database, self)

		#init with all users
		self.users = []
		self.update_users()

	def update_users(self):
		self.users = list(map(lambda result: result["_id"], self.user_db.db.find({})))

	def db_ping(self):
		return self.database.list_collection_names()

password = os.environ['MONGODB_PASSWORD']
dbname = os.environ['MONGODB_DBNAME']
username = os.environ["MONGODB_USER"]
clustername = os.environ["MONGODB_CLUSTER"]

db = Database(password, dbname, username, clustername)
