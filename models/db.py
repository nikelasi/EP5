import os
import pymongo
import random
import threading
import asyncio
import time
import datetime
from discord import Embed
from models.constants import embed_colour


class PrefixData:
	"""Class to handle prefix data"""
	data_key = "prefixes"
	def __init__(self, db):
		self.db = db[self.data_key]

	def get_prefix(self, client, message):

		prefix_db = self.db
		prefix_entry = prefix_db.find_one(
			{
				"_id": f"{message.guild.id}"
			}
		)

		if not prefix_entry:
			prefix_entry = prefix_db.find_one({"_id": "default"})
		return prefix_entry["prefix"]

	def set_prefix(self, guild_id, prefix):

		prefix_db = self.db
		prefix_entry = prefix_db.find_one({"_id": f"{guild_id}"})
		if not prefix_entry:

			prefix_db.insert_one(
				{
					"_id": f"{guild_id}",
					"prefix": f"{prefix}"
				}
			)
			return

		prefix_db.update_one(
			{
				"_id": f"{guild_id}"
			},
			{
				'$set': {
					"prefix": f"{prefix}"
				}
			}
		)
		return

class UserData:
	"""Class that handles user data"""
	data_key = "users"
	def __init__(self, db, parent_db):
		self.db = db[self.data_key]
		self.parent = parent_db
		
	def create_user(self, user_id, guild_id):
		user = {
			"_id": f"{guild_id}-{user_id}",
			"money": 0,
			"bank": {
				"money": 0,
				"interest": 0.01,
				"last_seen": 0
			},
			"rewards": {
				"daily": 0,
				"hourly": 0
			},
			"prestige": 0
		}
		try:
			_ = self.db.insert_one(user)
			self.parent.update_users()
			return 1
		except Exception as e:
			print(e)
			return None

	def fetch_user(self, user_id, guild_id):
		return self.db.find_one({"_id": f"{guild_id}-{user_id}"})

	def update_user_set_fields(self, _filter, fields):

		fields_to_set = {}
		for field, value in fields:
			fields_to_set[field] = value

		result = self.db.update_one(
			_filter,
			{"$set": fields_to_set}
		)

		return bool(result.matched_count) and bool(result.modified_count)

	def fetch_user_of(self, guild_id):
		return list(self.db.find({"_id": {"$regex": f"^{guild_id}-"}}))

class ItemsData:
	"""Class handling item data"""
	data_key = "items"
	def __init__(self, db, parent_db):
		self.db = db[self.data_key]
		self.parent = parent_db

	def fetch_items_of(self, guild_id):
		return list(self.db.find({"server_id": f"{guild_id}"}))

	def fetch_user_items(self, user_id):
		return list(self.db.find({f"owners.{user_id}": {"$exists": True}}))

	def fetch_item_named(self, item_name, guild_id):
		return self.db.find_one({"server_id": f"{guild_id}", "name": item_name})

	def set_items_of(self, guild_id, user_id, item_name, new_item_count, new_supply_count):

		fields = {f"owners.{user_id}": new_item_count}
		if new_supply_count: fields["supply"] = new_supply_count

		result = self.db.update_one(
			{"name": item_name, "server_id": f"{guild_id}"},
			{"$set": fields}
		)
		success = (bool(result.matched_count) and bool(result.modified_count))

		return {
			"success": success,
			"item": item_name,
			"new_count": new_item_count
		}

	async def update_items_price(self, guild_data):
		guild_id = guild_data['id']
		messages_info = guild_data['info']
		guild = guild_data['guild']

		results = self.fetch_items_of(guild_id)
		if len(results) == 0: return
		_ = await asyncio.gather(*[ItemsData.update_item_price_of(result, self.db, guild_id) for result in results])

		try:
			
			webhook_id = list(filter(lambda info: info['type'] == "prices_webhook", messages_info))[0]['id']
			webhooks = guild_data['webhooks']
			webhook = list(filter(lambda wh: str(wh.id) == webhook_id, webhooks))[0]
			prices_message = list(filter(lambda info: info['type'] == "prices_message", messages_info))

			avatar_url = "https://media.discordapp.net/attachments/677821942136438814/797686016411697162/eps_prices.png?width=1024&height=1024"
			username = "ΣP5 Prices"
			embed = Embed(
				colour=embed_colour
			)
			for item in self.fetch_items_of(guild_id):
				min_price = round(item['multipliers'][0]/100 * item['avg_price'])
				max_price = round(item['multipliers'][1]/100 * item['avg_price'])
				max_count = item['max']
				profit = round(max_count*max_price*0.8) - round(max_count*min_price)
				profitability = "Low" if profit < 300 else "Moderate" if profit < 2000 else "High"
				embed.add_field(name=item['name'], value=f"**{item['cost']} Σ** [**{min_price} Σ** ~ **{max_price} Σ**]\n{profitability} Profitability [**{profit} Σ**]")
			_now, _next = time.time(), (time.time() + 15*60)
			_now = datetime.datetime.fromtimestamp(_now).strftime('%e %b %I:%M %p')
			_next = datetime.datetime.fromtimestamp(_next).strftime('%e %b %I:%M %p')
			embed.set_footer(text=f"Last Updated: {_now}\nNext Update: {_next}")
			
			if prices_message:
				prices_message_id = prices_message[0]['id']
				await webhook.edit_message(message_id=int(prices_message_id), embed=embed)
			else:
				msg = await webhook.send(embed=embed, username=username, avatar_url=avatar_url, wait=True)
				self.parent.message_info_db.insert_prices_message(guild_id, msg.id)
				

		except IndexError:
			print("cant find")
			pass
		

	@staticmethod
	async def update_item_price_of(result, db, guild_id):
		min_multipler, max_multiplier = result['multipliers']
		multiplier = random.randint(int(min_multipler), int(max_multiplier))
		new_cost = round(result['avg_price'] * (multiplier/100))
		db.update_one(
			{"name": result["name"], "server_id": f"{guild_id}"},
			{"$set": {f"cost": new_cost}}
		)
		print(f"Updated `{result['name']}` cost from {result['cost']} to {new_cost}")
		return True


	def remove_item_from_owner(self, guild_id, user_id, item_name, new_supply_count):

		update_query = {"$unset": {f"owners.{user_id}": 0}}
		if new_supply_count: update_query["$set"] = {"supply": new_supply_count}

		result = self.db.update_one(
			{"name": item_name, "server_id": f"{guild_id}"},
			update_query
		)
		success = (bool(result.matched_count) and bool(result.modified_count))
		return {
			"success": success,
		}

class MessageInfoData:
	"""Class Handling Message Info Data"""
	data_key = "message_info"
	def __init__(self, db, parent_db):
		self.db = db[self.data_key]
		self.parent = parent_db

	def fetch_all(self):
		return list(self.db.find({}))

	def insert_prices_message(self, guild_id, _id):
		data = {
			"server_id": f"{guild_id}",
			"type": "prices_message",
			"id": f"{_id}"
		}
		try:
			_ = self.db.insert_one(data)
			return 1
		except Exception as e:
			print(e)
			return None

class Database:
	"""Class to handle the whole database"""
	def __init__(self, password, dbname, username, clustername):
		self.password = password
		self.dbname = dbname
		self.username = username
		self.clustername = clustername
		self.cluster = pymongo.MongoClient(f"mongodb+srv://{self.username}:{self.password}@{self.clustername}.jhxcv.mongodb.net/{self.dbname}?retryWrites=true&w=majority")
		self.database = self.cluster[self.dbname]

		self.prefix_db = PrefixData(self.database)
		self.user_db = UserData(self.database, self)
		self.items_db = ItemsData(self.database, self)
		self.message_info_db = MessageInfoData(self.database, self)

		#init with all users
		self.users = []
		self.update_users()

	def update_users(self):
		self.users = list(map(lambda result: result["_id"], self.user_db.db.find({})))

	def db_ping(self):
		return self.database.list_collection_names()

if __name__ != "db":
	password = os.environ['MONGODB_PASSWORD']
	dbname = os.environ['MONGODB_DBNAME']
	username = os.environ["MONGODB_USER"]
	clustername = os.environ["MONGODB_CLUSTER"]

	db = Database(password, dbname, username, clustername)
