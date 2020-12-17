import discord
from discord.ext import commands
from models.constants import banned_transfers, embed_colour
from models.db import db
from models.parser import UserDataParser

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
		sender_user = UserDataParser(user)
		user = db.user_db.fetch_user(receiver.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Who is this <@!{receiver.id}> you speak of? Never heard of them, hold on.\nPlease try again later")
		receiver_user = UserDataParser(user)

		if sender_user.get_user_money() < amount: return await msg.edit(content=f"You only have **{sender_user.get_user_money()} Σ**,\nyou cannot afford to send **{amount} Σ**!")

		await msg.edit(content="processing payment...")
		result = UserDataParser.process_payment(amount, sender_user, receiver_user, db.user_db)
		if not (result["receiver_updated"] and result["sender_updated"]): return await msg.edit(content=f"Something went wrong while processing the payment, try again later")
		
		embed = discord.Embed(
			description=f"You have sent **{result['amount']} Σ** to <@!{receiver.id}>!\n<@!{sender.id}>\'s balance: **{result['sender_balance']} Σ**\n<@!{receiver.id}>\'s balance: **{result['receiver_balance']} Σ**",
			colour=embed_colour
		)
		embed.set_author(name=f"Payment success")
		return await msg.edit(content=None, embed=embed)

	@pay.error
	async def pay_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Please fill in the required arguments! Check `{ctx.prefix}help pay`")

	@commands.command()
	async def bank(self, ctx, cmdtype, amount=None):
		msg = await ctx.send("processing...")
		if not cmdtype.lower() in ["info", "withdraw", "deposit"]: return await msg.edit(content=f"`{cmdtype}` is none of the following:\n- `info`\n- `withdraw`\n- `deposit`\ndo `{ctx.prefix}help bank` for more info")
		
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserDataParser(user)
		interest_result = user_parser.process_bank_interest(db.user_db)
		if interest_result == 0:
			interest_result = False
		else:
			if not interest_result["success"]:
				print("interest update unsuccessful")
			embed = discord.Embed(
				description=f"You earned **{interest_result['interest']} Σ** interest within the last **{interest_result['hours']} hours**!",
				colour=embed_colour
			)
			await ctx.send(embed=embed)

		if cmdtype.lower() == "info":
			embed = discord.Embed(
				description=f"**Bank Info**",
				colour=embed_colour
			)
			embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url) #pylint: disable=E1101
			embed.add_field(name="Balance", value=f"**{user_parser.get_bank_money()} Σ**", inline=True)
			return await msg.edit(content=None, embed=embed)

		elif cmdtype.lower() == "withdraw":

			if not amount: return await msg.edit(content="Withdraw how much? 1000? 20?\nPlease specify the amount you want to withdraw!")
			try:
				amount = int(amount)
			except ValueError:
				return await msg.edit(content=f"Does {amount} look like an integer to you?")

			if amount == 0: return await msg.edit(content="Please don\'t waste my resources doing a pointless task!")
			if amount < 0: return await msg.edit(content=f"Are you trying to be a joker?")
			if user_parser.get_bank_money() < amount: return await msg.edit(content=f"Your bank balance is **{user_parser.get_bank_money()} Σ**!\nYou cannot possibly withdraw more than you have!")

			result = user_parser.process_bank_ops("withdraw", amount, db.user_db)
			if not result["success"]: return await msg.edit(content=f"Something went wrong while withdrawing, try again later")

			embed = discord.Embed(
				description=f"You have withdrawn **{result['amount']} Σ** from the bank!\nNew User Balance: **{result['new_user_bal']} Σ**\nNew Bank Balance: **{result['new_bank_bal']} Σ**",
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
			if user_parser.get_user_money() < amount: return await msg.edit(content=f"Your user balance is **{user_parser.get_user_money()} Σ**!\nYou cannot possibly deposit more than you have!")

			result = user_parser.process_bank_ops("deposit", amount, db.user_db)
			if not result["success"]: return await msg.edit(content=f"Something went wrong while depositing, try again later")

			embed = discord.Embed(
				description=f"You have deposited **{result['amount']} Σ** in the bank!\nNew User Balance: **{result['new_user_bal']} Σ**\nNew Bank Balance: **{result['new_bank_bal']} Σ**",
				colour=embed_colour
			)
			embed.set_author(name=f"Bank Deposition")
			return await msg.edit(content=None, embed=embed)

		return await msg.edit(content=f"You somehow broke the system!")

	@bank.error
	async def bank_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Please pass in all required arguments, check `{ctx.prefix}help bank` for more info.")

def setup(client):
	client.add_cog(economy(client))
