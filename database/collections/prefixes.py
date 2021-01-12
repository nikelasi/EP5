class Database:
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