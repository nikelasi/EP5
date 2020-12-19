import random, enum
import discord
from discord.ext import commands
from models.constants import embed_colour
from models.db import db
from models.parser import UserDataParser

class Coinflip(enum.Enum):
	HEADS = "Heads"
	TAILS = "Tails"

class fun(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["flip", "cf"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def coinflip(self, ctx, heads_or_tails=None, bet=None):

		msg = await ctx.send("flipping coin...")
		probability = random.randrange(452, 558+1)
		tails_percentage, heads_percentage, heads_threshold = f"{100 - (probability/10)}%", f"{probability/10}%", probability/1000
		coinflip_result = random.random()
		result = Coinflip.HEADS
		if coinflip_result > heads_threshold:
			result = Coinflip.TAILS

		embed = discord.Embed(
			description=f"{tails_percentage} of flipping tails\n{heads_percentage} of flipping heads",
			colour=embed_colour
		)
		embed.set_author(name="Coinflip")
		embed.add_field(name="Result", value=result.value, inline=True)
		
		if not heads_or_tails and not bet: return await msg.edit(content=None, embed=embed)
		await msg.edit(content="doing checks...")

		if not heads_or_tails.capitalize() in [possibility.value for possibility in Coinflip]: return await msg.edit(content=f"`{heads_or_tails.capitalize()}` is neither any of the following: {', '.join(map(lambda x: f'`{x}`', [result.value for result in Coinflip]))}")
		guess = {True: "correct", False: "wrong"}.get(heads_or_tails.capitalize() == result.value)
		embed.description = f"{embed.description}\nYour guess was {guess}!"
		embed.add_field(name="Guess", value=heads_or_tails.capitalize(), inline=True)
		if not bet: return await msg.edit(content=None, embed=embed)

		try:
			bet = int(bet)
		except ValueError:
			return await msg.edit(content=f"What does betting `{bet}` even mean? Does `{bet}` look like an integer to you?")

		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserDataParser(user)
		user_balance = user_parser.get_user_money()

		if bet == 0: return await msg.edit(content="If you want to bet nothing, just don\'t include the number next time")
		if bet < 0: return await msg.edit(content=f"No no, you think I forgot about checking it?")
		if user_balance < bet: return await msg.edit(content=f"Your user balance is **{user_balance} Σ**!\nYou cannot possibly bet more than you have!")

		new_balance, win_indicator = {"correct": (user_balance+bet, f"\nYou won **{bet} Σ**"), "wrong": (user_balance-bet, f"\nYou lost **{bet} Σ**")}.get(guess)
		success = {
			"correct": user_parser.update_user_money(new_balance, db.user_db),
			"wrong": user_parser.update_user_money(new_balance, db.user_db)
		}.get(guess)

		embed.description += win_indicator
		embed.add_field(name="Balance", value=f"**{new_balance} Σ**", inline=True)
		return await msg.edit(content=None, embed=embed)


	@coinflip.error
	async def coinflip_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"please pass in all the required arguments, check `{ctx.prefix}help coinflip` for more info")

def setup(client):
	client.add_cog(fun(client))