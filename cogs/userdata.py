import discord
from discord.ext import commands
from models.db import db
from models.parser import UserDataParser
from models.constants import embed_colour

class userdata(commands.Cog):
	"""cog to store commands related to userdatay"""
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["lb", "ldb"])
	async def leaderboard(self, ctx):
		msg = await ctx.send("fetching user data...")
		users = db.user_db.fetch_user_of(ctx.guild.id)
		if not bool(len(users)):
			return await msg.edit(content=f"Apparently, there are no users registered in this server\nTry again later")
		await msg.edit(content="processing user data...")
		lb = ""
		users = sorted(users, key=lambda k: k["money"], reverse=True)
		ranking = 0
		for user in users:
			ranking += 1
			parser = UserDataParser(user)
			lb += f"{ranking}) <@!{parser.get_id()[1]}> - **{parser.get_user_money()} Σ**\n"

		embed = discord.Embed(
			description=lb,
			colour=embed_colour
		)

		embed.set_author(name=f"Leaderboard")
		return await msg.edit(content=None, embed=embed)

	@leaderboard.error
	async def leaderboard_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Please pass in all the required arguments!")

	@commands.command(aliases=["stats", "user", "bal"])
	async def stat(self, ctx, member: discord.Member):
		if member:
			msg = await ctx.send("processing data...")
			user = db.user_db.fetch_user(member.id, ctx.guild.id)
			if not user:
				return await msg.edit(content=f"<@!{member.id}> is not registered in the bot\'s database\nTry again later")
			data_parser = UserDataParser(user)
			await msg.edit(content="fetching user data...")

			embed = discord.Embed(
				colour=embed_colour
			)

			embed.add_field(name="User", value=f"Balance: **{data_parser.get_user_money()} Σ**")
			embed.add_field(name="Others", value=f"ServerID: `{data_parser.get_id()[0]}`\nUserID: `{data_parser.get_id()[1]}`")
			embed.set_author(name=f"{member}", icon_url=member.avatar_url)
			return await msg.edit(content=None, embed=embed)

		return await ctx.send("You did not specify a member!")

	@stat.error
	async def stat_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			msg = await ctx.send("processing data...")
			user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
			if not user:
				return await msg.edit(content=f"You are not registered in the bot\'s database\nTry again later")
			data_parser = UserDataParser(user)
			await msg.edit(content="fetching user data...")

			embed = discord.Embed(
				colour=embed_colour
			)

			embed.add_field(name="User", value=f"Balance: **{data_parser.get_user_money()} Σ**")
			embed.add_field(name="Others", value=f"ServerID: `{data_parser.get_id()[0]}`\nUserID: `{data_parser.get_id()[1]}`")
			embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
			return await msg.edit(content=None, embed=embed)

		elif isinstance(error, commands.MemberNotFound): #pylint: disable=E1101
			await ctx.send(f"The member you specified isn\'t a discord member!")


def setup(client):
	client.add_cog(userdata(client))
