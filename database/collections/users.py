class Database:
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