from database.db import db

class ItemData:
	def __init__(self, data):
		self.item_data = data
		self.owners_data = self.item_data['owners']
		self.server_id = self.item_data['server_id']
		self.multipliers = self.item_data['multipliers']
		self.name = self.item_data['name']
		self.description = self.item_data['description']
		self.max_owned = self.item_data['max']
		self.supply = self.item_data['supply']
		self.average_price = self.item_data['avg_price']
		self.cost = self.item_data['cost']

	def get_cumul_cost_of(self, amount):
		return self.cost*amount

	def get_amount_owned_by(self, owner_id):
		id_key = f"{self.server_id}-{owner_id}"
		return self.owners_data[id_key]

	def update_fields(self, fields):
		return db.items_db.db.update_one(
			{"server_id": f"{self.server_id}", "name": f"{self.name}"},
			fields
		)

