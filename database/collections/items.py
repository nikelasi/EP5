import random, asyncio, time, datetime
from discord import Embed
from configs.settings import embed_colour

class Database:
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
		results = list(filter(lambda item: item['name'] != "Real Life $1 SGD", results))
		_ = await asyncio.gather(*[self.__class__.update_item_price_of(result, self.db, guild_id) for result in results])

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
			
			time_offset = 28800
			_now, _next = (time.time() + time_offset), ((time.time() + 15*60) + time_offset)
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