import time
from database.db import db

def process_bank_ops(user_data, withdraw_or_deposit, amount):
	bank_money, user_money = user_data.bank_data["money"], user_data.user_data["money"]
	if withdraw_or_deposit == "withdraw":
		bank_money -= amount
		user_money += amount
	elif withdraw_or_deposit == "deposit":
		bank_money += amount
		user_money -= amount

	success = db.user_db.update_user_set_fields(
		{"_id": user_data.user_data["_id"]},
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

def process_bank_interest(user_data):
	last_seen = user_data.bank_data["last_seen"]
	bank_money = user_data.bank_data["money"]
	interest = user_data.bank_data["interest"]

	if last_seen == 0:
		db.user_db.update_user_set_fields(
			{"_id": user_data.user_data["_id"]},
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

	success = db.user_db.update_user_set_fields(
		{"_id": user_data.user_data["_id"]},
		[
			("bank.last_seen", new_last_seen),
			("bank.money", new_amount)
		]
	)

	if success:
		#update parser's info
		user_data.bank_data["money"] = new_amount
		user_data.bank_data["last_seen"] = new_last_seen

	return {
		"success": success,
		"hours": interest_iteration,
		"interest": new_amount - bank_money
	}

def process_payment(amount, sender, receiver):
	sender_money, receiver_money = sender.get_user_money(), receiver.get_user_money()
	sender_money -= amount
	receiver_money += amount

	sender_update_success = sender.update_user_money(sender_money)
	receiver_update_success = receiver.update_user_money(receiver_money)

	return {
		"receiver_updated": receiver_update_success,
		"sender_updated": sender_update_success,
		"amount": amount,
		"sender_balance": sender_money,
		"receiver_balance": receiver_money
	}