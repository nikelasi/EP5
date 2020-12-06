import pymongo, os
from pymongo import MongoClient

#environ
password = os.environ['MONGODB_PASSWORD']
dbname = os.environ['MONGODB_DBNAME']

#application
cluster = MongoClient(f"mongodb+srv://fgtEPSbot:{password}@eps.zv2oq.mongodb.net/{dbname}?retryWrites=true&w=majority")

#get db and prefixes collection
mongodb = cluster[dbname]
prefix_db = mongodb["prefixes"]

def get_prefix(client, message):
	prefix_entry = prefix_db.find_one({"_id": f"{message.guild.id}"})
	if not prefix_entry:
		prefix_entry = prefix_db.find_one({"_id": "default"})
	return prefix_entry["prefix"]

def set_prefix(guild_id, prefix):
	prefix_entry = prefix_db.find_one({"_id": f"{guild_id}"})
	if not prefix_entry:
		prefix_db.insert_one({"_id": f"{guild_id}", "prefix": f"{prefix}"})
		return
	prefix_db.update_one({"_id": f"{guild_id}"}, {'$set': {"prefix": f"{prefix}"}})
	return

def db_ping():
	_ = prefix_db.find_one({})
	return