import discord
from discord.ext import commands
from models.db import db
from models.parser import UserDataParser

class econ(commands.Cog):
	"""cog to store commands related to economy"""
	def __init__(self, client):
		self.client = client

	"""
	@commands.command()
	async def bank(self, ctx, cmdtype, val=None):
		if not cmdtype.lower() in ["info", "withdraw", "deposit"]:
			pass

	@bank.error
	async def bank_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Enter all required arguments!")
		else:
			await ctx.send(f"Error: {error}")
	"""

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
				description=f"""
				__User__
				= Balance: **{data_parser.get_user_money()} Σ**
				__Others__
				= ServerID: `{data_parser.get_id()[0]}`
				= UserID: `{data_parser.get_id()[1]}`
				""",
				colour=0x3bb300
			)

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
				description=f"""
				__User__
				= Balance: **{data_parser.get_user_money()} Σ**
				__Others__
				= ServerID: `{data_parser.get_id()[0]}`
				= UserID: `{data_parser.get_id()[1]}`
				""",
				colour=0x3bb300
			)

			embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
			return await msg.edit(content=None, embed=embed)
		elif isinstance(error, commands.MemberNotFound): #pylint: disable=E1101
			await ctx.send(f"The member you specified isn\'t a discord member!")


def setup(client):
	client.add_cog(econ(client))
