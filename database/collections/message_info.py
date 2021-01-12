
class Database:
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
