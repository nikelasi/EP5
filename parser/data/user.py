from database.db import db

class UserData:
	def __init__(self, data):
		self.user_data = data
		self.bank_data = self.user_data["bank"]
		self.rewards_data = self.user_data["rewards"]

	def get_id(self):
		_id = self.user_data["_id"]
		return _id.split("-")

	def get_user_money(self):
		return self.user_data["money"]

	def get_bank_money(self):
		return self.bank_data["money"]

	def get_interest_percent(self):
		return round(self.bank_data["interest"] * 100)

	def get_prestige(self):
		return int(self.user_data['prestige'])

	def update_user_money(self, new_amount):
		return db.user_db.update_user_set_fields(
			{"_id": self.user_data["_id"]},
			[("money", new_amount)]
		)

