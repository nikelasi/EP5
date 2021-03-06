import discord, asyncio
from discord.ext import commands
from configs.settings import banned_transfers, embed_colour
from database.db import db
from parser.parsers import UserData
from utils.economy import *
from utils.formulas import *

class economy(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["send"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def pay(self, ctx, receiver: discord.Member, amount):
		msg = await ctx.send("processing...")

		try:
			amount = int(amount)
		except ValueError:
			return await msg.edit(content=f"Does `{amount}` look like an integer to you?")

		sender = ctx.author
		if receiver.bot: return await msg.edit(content=f"Seriously? You expect a bot to be registered in my database?")
		if sender.id == receiver.id: return await msg.edit(content="What\'s the point of sending to yourself?\nStop wasting my resources!")
		if amount == 0: return await msg.edit(content="Scram! Stop wasting my resources to do a pointless task!")
		if amount < 0: return await msg.edit(content=f"You think you are funny?\nPaying people negative money?")

		for banned_transfer in banned_transfers:
			p1, p2 = banned_transfer
			if ((sender.id == p1 and receiver.id == p2) or (sender.id == p2 and receiver.id == p1)):
				return await msg.edit(content=f"ALT Account detected!\nNo cheating to the top of leaderboard!")

		await msg.edit(content=f"checking user data...")
		user = db.user_db.fetch_user(sender.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		sender_user = UserData(user)
		user = db.user_db.fetch_user(receiver.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Who is this <@!{receiver.id}> you speak of? Never heard of them, hold on.\nPlease try again later")
		receiver_user = UserData(user)

		if sender_user.get_user_money() < amount: return await msg.edit(content=f"You only have **{sender_user.get_user_money():,} Σ**,\nyou cannot afford to send **{amount:,} Σ**!")

		await msg.edit(content="processing payment...")
		result = process_payment(amount, sender_user, receiver_user)
		if not (result["receiver_updated"] and result["sender_updated"]): return await msg.edit(content=f"Something went wrong while processing the payment, try again later")
		
		embed = discord.Embed(
			description=f"You have sent **{result['amount']:,} Σ** to <@!{receiver.id}>!\n<@!{sender.id}>\'s balance: **{result['sender_balance']:,} Σ**\n<@!{receiver.id}>\'s balance: **{result['receiver_balance']:,} Σ**",
			colour=embed_colour
		)
		embed.set_author(name=f"Payment success")
		return await msg.edit(content=None, embed=embed)

	@pay.error
	async def pay_error(self, ctx, error):
		pass

	@commands.command(aliases=["bank_reset"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def reset_bank(self, ctx):
		msg = await ctx.send("processing...")
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"It appears that you don\'t exist to me. (No offense)\nPlease try again later")
		data_parser = UserData(user)

		embed = discord.Embed(
			title="Bank Reset",
			description=f"Are you sure you want to reset your bank money?\nNote: interest will stay\n",
			colour=embed_colour
		)

		await msg.edit(content=None, embed=embed)
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ["☑️", "🇽"]
		for reaction in ["☑️", "🇽"]: await msg.add_reaction(reaction)
		try:
			reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
		except asyncio.TimeoutError:
			return await msg.edit(content=f"You did not react within a 60s timespan, terminating prestige")

		await msg.clear_reactions()
		if str(reaction.emoji) == "🇽":
			return await msg.edit(content="Cancelled Bank Reset", embed=None)

		await msg.edit(content="processing reset...", embed=None)
		success = db.user_db.update_user_set_fields(
			{"_id": data_parser.user_data['_id']},
			[
				("bank.money", 0),
				("bank.last_seen", int(time.time()))
			]
		)

		if not success: return await msg.edit(content=f"Something went wrong while resetting your bank money, try again later")

		embed = discord.Embed(
			title=f"Bank Reset Successful",
			description=f"Your bank reset have been successful!",
			colour=embed_colour
		)

		return await msg.edit(content=None, embed=embed)

	@reset_bank.error
	async def bank_reset_error(self, ctx, error):
		pass

	@commands.command()
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def bank(self, ctx, cmdtype, amount=None):
		msg = await ctx.send("processing...")
		if not cmdtype.lower() in ["info", "withdraw", "deposit", "stats", "stat", "upgrade"]: return await msg.edit(content=f"`{cmdtype}` is none of the following:\n- `info`\n- `withdraw`\n- `deposit`\n- `upgrade`\ndo `{ctx.prefix}help bank` for more info")
		
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserData(user)
		interest_result = process_bank_interest(user_parser)
		if interest_result == 0:
			interest_result = False
		else:
			if not interest_result["success"]:
				print("interest update unsuccessful")
			embed = discord.Embed(
				description=f"You earned **{interest_result['interest']:,} Σ** interest within the last **{interest_result['hours']:,} hours**!",
				colour=embed_colour
			)
			await ctx.send(embed=embed)

		if cmdtype.lower() in ["info", "stats", "stat"]:
			money_to_upgrade = get_interest_cost(user_parser.get_interest_percent())
			embed = discord.Embed(
				title="Bank Info",
				description=f"**{money_to_upgrade:,} Σ** to upgrade to {user_parser.get_interest_percent()+1}% interest",
				colour=embed_colour
			)
			embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url) #pylint: disable=E1101
			if (user_parser.get_user_money() + user_parser.get_bank_money()) < money_to_upgrade: embed.description = f"{embed.description}\nYou can\'t afford the upgrade yet"
			else: embed.description = f"{embed.description}\nYou can afford the upgrade, make sure **{money_to_upgrade:,} Σ** is in the bank\nand run `{ctx.prefix}bank upgrade`"
			embed.add_field(name="Interest", value=f"**{user_parser.get_interest_percent()}%**", inline=True)
			embed.add_field(name="Balance", value=f"**{user_parser.get_bank_money():,} Σ**", inline=True)
			return await msg.edit(content=None, embed=embed)

		elif cmdtype.lower() == "upgrade":
			money_to_upgrade = get_interest_cost(user_parser.get_interest_percent())
			if user_parser.get_bank_money() < money_to_upgrade: return await msg.edit(content=f"Bank interest upgrade from {user_parser.get_interest_percent()}% to {user_parser.get_interest_percent()+1}% failed because,\nYou only have **{user_parser.get_bank_money():,} Σ** in your bank when you need **{money_to_upgrade:,} Σ** to upgrade.")
			success = db.user_db.update_user_set_fields(
				{"_id": user_parser.user_data["_id"]},
				[
					("bank.money", (user_parser.get_bank_money() - money_to_upgrade)),
					("bank.interest", ((user_parser.get_interest_percent()+1)/100))
				]
			)
			if not success: return await msg.edit(content=f"Something went wrong while upgrading your interest, try again later")
			embed = discord.Embed(
				description=f"Successfully upgraded to {user_parser.get_interest_percent()+1}% for a cost of **{money_to_upgrade:,} Σ**\nNew Bank Balance: **{(user_parser.get_bank_money()-money_to_upgrade):,} Σ**\nNew Bank Interest: **{user_parser.get_interest_percent()+1}%**",
				colour=embed_colour
			)
			embed.set_author(name=f"Interest Upgrade")
			return await msg.edit(content=None, embed=embed)

		elif cmdtype.lower() == "withdraw":

			if not amount: return await msg.edit(content="Withdraw how much? 1000? 20?\nPlease specify the amount you want to withdraw!")
			try:
				amount = int(amount)
			except ValueError:
				return await msg.edit(content=f"Does {amount} look like an integer to you?")

			if amount == 0: return await msg.edit(content="Please don\'t waste my resources doing a pointless task!")
			if amount < 0: return await msg.edit(content=f"Are you trying to be a joker?")
			if user_parser.get_bank_money() < amount: return await msg.edit(content=f"Your bank balance is **{user_parser.get_bank_money():,} Σ**!\nYou cannot possibly withdraw more than you have!")

			result = process_bank_ops(user_parser, "withdraw", amount)
			if not result["success"]: return await msg.edit(content=f"Something went wrong while withdrawing, try again later")

			embed = discord.Embed(
				description=f"You have withdrawn **{result['amount']:,} Σ** from the bank!\nNew User Balance: **{result['new_user_bal']:,} Σ**\nNew Bank Balance: **{result['new_bank_bal']:,} Σ**",
				colour=embed_colour
			)
			embed.set_author(name=f"Bank Withdrawal")
			return await msg.edit(content=None, embed=embed)

		elif cmdtype.lower() == "deposit":

			if not amount: return await msg.edit(content="Deposit how much? 1000? 20?\nPlease specify the amount you want to deposit!")
			try:
				amount = int(amount)
			except ValueError:
				return await msg.edit(content=f"Does {amount} look like an integer to you?")

			if amount == 0: return await msg.edit(content="Please don\'t waste my resources doing a pointless task!")
			if amount < 0: return await msg.edit(content=f"Are you trying to be a joker?")
			if user_parser.get_user_money() < amount: return await msg.edit(content=f"Your user balance is **{user_parser.get_user_money():,} Σ**!\nYou cannot possibly deposit more than you have!")

			result = process_bank_ops(user_parser, "deposit", amount)
			if not result["success"]: return await msg.edit(content=f"Something went wrong while depositing, try again later")

			embed = discord.Embed(
				description=f"You have deposited **{result['amount']:,} Σ** in the bank!\nNew User Balance: **{result['new_user_bal']:,} Σ**\nNew Bank Balance: **{result['new_bank_bal']:,} Σ**",
				colour=embed_colour
			)
			embed.set_author(name=f"Bank Deposition")
			return await msg.edit(content=None, embed=embed)

		return await msg.edit(content=f"You somehow broke the system!")

	@bank.error
	async def bank_error(self, ctx, error):
		pass

def setup(client):
	client.add_cog(economy(client))
