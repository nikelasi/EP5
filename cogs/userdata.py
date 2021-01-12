import discord, asyncio
from discord.ext import commands
from database.db import db
from parser.parsers import UserData
from configs.settings import embed_colour

class userdata(commands.Cog):
	"""cog to store commands related to userdatay"""
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["lb", "ldb"])
	async def leaderboard(self, ctx):
		msg = await ctx.send("fetching user data...")
		users = db.user_db.fetch_user_of(ctx.guild.id)
		if not bool(len(users)):
			return await msg.edit(content=f"And I thought this server was empty! How am I here?\nPlease try again later")
		await msg.edit(content="processing user data...")
		lb = ""
		users = sorted(users, key=lambda k: k["money"], reverse=True)
		ranking = 0
		for user in users:
			ranking += 1
			parser = UserData(user)
			lb += f"{ranking}) <@!{parser.get_id()[1]}> - **{parser.get_user_money():,} Σ**\n"

			if ranking == 10: break

		embed = discord.Embed(
			description=lb,
			colour=embed_colour
		)

		embed.set_author(name=f"Leaderboard")
		return await msg.edit(content=None, embed=embed)

	@leaderboard.error
	async def leaderboard_error(self, ctx, error):
		pass

	@commands.command(aliases=["stats", "user", "bal"])
	async def stat(self, ctx, member: discord.Member = None):
		msg = await ctx.send("processing data...")
		if member:
			if member.bot:
				return await msg.edit(content=f"Very funny, you know <@!{member.id}> is a bot.")
			user = db.user_db.fetch_user(member.id, ctx.guild.id)
			if not user:
				return await msg.edit(content=f"<@!{member.id}> exists? Never heard of them, hold on.\nPlease try again later")
			data_parser = UserData(user)
			await msg.edit(content="fetching user data...")

			embed = discord.Embed(
				colour=embed_colour
			)

			embed.add_field(name="User", value=f"Balance: **{data_parser.get_user_money():,} Σ**\nPrestige **Rank {data_parser.get_prestige()+1}** [{1 if data_parser.get_prestige() == 0 else (1+(data_parser.get_prestige()*0.75))}x Reward Multiplier]")
			embed.add_field(name="Others", value=f"ServerID: `{data_parser.get_id()[0]}`\nUserID: `{data_parser.get_id()[1]}`")
			embed.set_author(name=f"{member}", icon_url=member.avatar_url)
			return await msg.edit(content=None, embed=embed)

		#return await ctx.send(f"Good job lmao. You broke the system")
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user:
			return await msg.edit(content=f"It appears that you don\'t exist to me. (No offense)\nPlease try again later")
		data_parser = UserData(user)
		await msg.edit(content="fetching user data...")

		embed = discord.Embed(
			colour=embed_colour
		)

		embed.add_field(name="User", value=f"Balance: **{data_parser.get_user_money():,} Σ**\nPrestige Rank **{data_parser.get_prestige()+1}** [{0 if data_parser.get_prestige() == 0 else (1+(data_parser.get_prestige()*0.75))}x Reward Multiplier]")
		embed.add_field(name="Others", value=f"ServerID: `{data_parser.get_id()[0]}`\nUserID: `{data_parser.get_id()[1]}`")
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
		return await msg.edit(content=None, embed=embed)

	@stat.error
	async def stat_error(self, ctx, error):
		pass

	@commands.command(aliases=["pres"])
	async def prestige(self, ctx):
		msg = await ctx.send("processing data...")
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"It appears that you don\'t exist to me. (No offense)\nPlease try again later")
		data_parser = UserData(user)

		prestige_cost = round(100000 * ((data_parser.get_prestige()+1)*1.25))

		embed = discord.Embed(
			title="Prestige Info",
			description=f"When you prestige:\n1. Rewards multiplier will be increased by 0.75\n2. Flex more about how no life you are\n",
			colour=embed_colour
		)
		embed.add_field(name="Current Rank", value=f"**Rank {data_parser.get_prestige()+1}**")
		embed.add_field(name="Cost", value=f"**{prestige_cost:,} Σ**")	
		user_money = data_parser.get_user_money()
		if user_money < prestige_cost:
			embed.description += f"Looks like you don\'t have enough **Σ** to prestige, try again when you have **{prestige_cost:,} Σ**!"
			return await msg.edit(content=None, embed=embed)
		
		embed.description += f"You are eligible to prestige to Rank {data_parser.get_prestige()+2}, react with ☑️ to confirm ranking up or react with 🇽 to decline."
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
			return await msg.edit(content="Declined Rank Up", embed=None)

		await msg.edit(content="processing rank", embed=None)
		success = db.user_db.update_user_set_fields(
			{"_id": data_parser.user_data['_id']},
			[
				("money", user_money - prestige_cost),
				("prestige", data_parser.get_prestige()+1)
			]
		)

		if not success: return await msg.edit(content=f"Something went wrong while ranking up, try again later")

		embed = discord.Embed(
			title=f"Ranked Up Successfully",
			description=f"You have ranked up to **Rank {data_parser.get_prestige()+2}**\nYour new rewards multiplier is {1+(0.75*(data_parser.get_prestige()+1))}x",
			colour=embed_colour
		)

		return await msg.edit(content=None, embed=embed)


	@prestige.error
	async def prestige_error(self, ctx, error):
		pass


def setup(client):
	client.add_cog(userdata(client))
