import time

class ProcessingTools:
	def __init__(self):
		pass

	@staticmethod
	def seconds_to_time(seconds):

		days = (seconds // (60*60*24)), "day"
		seconds %= (60*60*24)

		hours = (seconds // (60*60)), "hour"
		seconds %= (60*60)

		minutes = (seconds // (60)), "minute"
		seconds = seconds % 60, "second"

		_time = []
		for u, m in [days, hours, minutes, seconds]:
			if u:
				if u > 1:
					m += "s"
				_time.append(f"{u} {m}")

		return ", ".join(_time)

	@staticmethod
	def price_to_increment_interest(current_interest):
		#formula: 70,000(interest)^1.5
		needed = int(round(70_000*current_interest**(current_interest*0.35), -3))
		return needed

class UserDataParser:
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

	def process_bank_ops(self, withdraw_or_deposit, amount, user_db):
		bank_money, user_money = self.bank_data["money"], self.user_data["money"]
		if withdraw_or_deposit == "withdraw":
			bank_money -= amount
			user_money += amount
		elif withdraw_or_deposit == "deposit":
			bank_money += amount
			user_money -= amount

		success = user_db.update_user_set_fields(
			{"_id": self.user_data["_id"]},
			[
				("bank.money", bank_money),
				("money", user_money)
			]
		)

		return {
			"success": success,
			"amount": amount,
			"new_bank_bal": bank_money,
			"new_user_bal": user_money
		}

	def process_bank_interest(self, user_db):
		last_seen = self.bank_data["last_seen"]
		bank_money = self.bank_data["money"]
		interest = self.bank_data["interest"]

		if last_seen == 0:
			user_db.update_user_set_fields(
				{"_id": self.user_data["_id"]},
				[
					("bank.last_seen", int(time.time()))
				]
			)
			return 0
		elif bank_money == 0:
			return 0
		
		period = 60*60 #3600s AKA 1h
		current_time = int(time.time())
		time_since_last_seen = current_time - last_seen
		interest_iteration = time_since_last_seen // period

		if interest_iteration == 0:
			return 0

		time_offset = time_since_last_seen % period
		new_last_seen = current_time - time_offset
		# A = P(1 + 0.01)**t
		new_amount = int(bank_money*((1 + interest)**interest_iteration))
		compound_interest = new_amount - bank_money

		if compound_interest == 0 or new_amount == bank_money:
			return 0

		success = user_db.update_user_set_fields(
			{"_id": self.user_data["_id"]},
			[
				("bank.last_seen", new_last_seen),
				("bank.money", new_amount)
			]
		)

		if success:
			#update parser's info
			self.bank_data["money"] = new_amount
			self.bank_data["last_seen"] = new_last_seen

		return {
			"success": success,
			"hours": interest_iteration,
			"interest": new_amount - bank_money
		}

	@staticmethod
	def process_payment(amount, sender, receiver, user_db):
		sender_money, receiver_money = sender.get_user_money(), receiver.get_user_money()
		sender_money -= amount
		receiver_money += amount

		sender_update_success = sender.update_user_money(sender_money, user_db)
		receiver_update_success = receiver.update_user_money(receiver_money, user_db)

		return {
			"receiver_updated": receiver_update_success,
			"sender_updated": sender_update_success,
			"amount": amount,
			"sender_balance": sender_money,
			"receiver_balance": receiver_money
		}

	def update_user_money(self, new_amount, user_db):
		return user_db.update_user_set_fields(
			{"_id": self.user_data["_id"]},
			[("money", new_amount)]
		)

	def process_user_rewards(self, reward_details, user_db):

		_type, _period, _prize = reward_details
		now = int(time.time())
		last_collected = self.rewards_data[_type]
		timeframe = now-last_collected

		multiplier = 1
		if self.get_prestige() != 0:
			multiplier += (0.75*(self.get_prestige()))
		_prize = round(_prize * multiplier)

		if timeframe // _period > 0: #eligible for rewards
			new_amount = self.user_data["money"] + _prize
			success = user_db.update_user_set_fields(
				{"_id": self.user_data["_id"]},
				[
					(f"rewards.{_type}", now),
					(f"money", new_amount)
				]
			)

			return {
				"eligible": True,
				"update_status": success,
				"prize": _prize,
				"next_reward": ProcessingTools.seconds_to_time(_period)
			}

		next_collection_time = last_collected + _period
		time_to_collection = next_collection_time - now

		return {
			"eligible": False,
			"next_reward": ProcessingTools.seconds_to_time(time_to_collection)
		}


"""
{
	'_id': '509667665401610251-348307478808756224',
	'money': 0,
	'bank': {
		'money': 0,
		'interest': 0,
		'last_seen': 0
	},
	'rewards': {
		'daily': 0,
		'hourly': 0
	}
}
"""
