import random
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
		elif isinstance(error, commands.MemberNotFound):
			await ctx.send(f"The member you specified isn\'t a discord member!")
		else:
			await ctx.send(f"Error: {error}")

	@commands.command()
	async def hourly(self, ctx):
		msg = await ctx.send(f"fetching your user data...")
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user:
			return await msg.edit(content=f"<@!{ctx.author.id}>, failed to fetch your user data, try again later.")
		data_parser = UserDataParser(user)
		await msg.edit(content="processing reward...")

		_type, _period, _prize = ("hourly", 60*60, random.randint(1, 20))
		reward_data = (_type, _period, _prize)

		process_results = data_parser.process_user_rewards(reward_data, db.user_db)

		if process_results["eligible"]:
			if process_results["update_status"]:
				embed = discord.Embed(
					description=f"**{_type.capitalize()} Reward**",
					colour=0x3bb300
				)

				embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
				embed.add_field(name="Reward", value=f"{_prize} Σ", inline=True)
				embed.add_field(name="Next Reward", value=f"{process_results['next_reward']}", inline=True)
				return await msg.edit(content=None, embed=embed)

			return await msg.edit(content="Something went wrong while redeeming the reward...\nTry again later.")

		embed = discord.Embed(
			description=f"<@!{data_parser.get_id()[1]}>, you already collected this,\nplease wait `{process_results['next_reward']}`",
			colour=0x3bb300
		)
		return await msg.edit(content=None, embed=embed)

	@hourly.error
	async def hourly_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Please fill in the required arguments!\nRefer to `{ctx.prefix}help`!")
		else:
			await ctx.send(f"Error: {error}")

	@commands.command()
	async def daily(self, ctx):
		msg = await ctx.send(f"fetching your user data...")
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user:
			return await msg.edit(content=f"<@!{ctx.author.id}>, failed to fetch your user data, try again later.")
		data_parser = UserDataParser(user)
		await msg.edit(content="processing reward...")

		_type, _period, _prize = ("daily", 60*60*24, random.randint(1, 300))
		reward_data = (_type, _period, _prize)

		process_results = data_parser.process_user_rewards(reward_data, db.user_db)

		if process_results["eligible"]:
			if process_results["update_status"]:
				embed = discord.Embed(
					description=f"**{_type.capitalize()} Reward**",
					colour=0x3bb300
				)

				embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
				embed.add_field(name="Reward", value=f"{_prize} Σ", inline=True)
				embed.add_field(name="Next Reward", value=f"{process_results['next_reward']}", inline=True)
				return await msg.edit(content=None, embed=embed)

			return await msg.edit(content="Something went wrong while redeeming the reward...\nTry again later.")

		embed = discord.Embed(
			description=f"<@!{data_parser.get_id()[1]}>, you already collected this,\nplease wait `{process_results['next_reward']}`",
			colour=0x3bb300
		)
		return await msg.edit(content=None, embed=embed)

	@daily.error
	async def daily_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Please fill in the required arguments!\nRefer to `{ctx.prefix}help`!")
		else:
			await ctx.send(f"Error: {error}")


def setup(client):
	client.add_cog(econ(client))
