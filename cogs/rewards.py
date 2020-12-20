import random
import discord
from discord.ext import commands
from models.db import db
from models.parser import UserDataParser
from models.constants import embed_colour

class RewardsCMDHandler:
	def __init__(self):
		pass

	async def process_reward(ctx, reward_data): #pylint: disable=E0213

		msg = await ctx.send(f"fetching your user data...") #pylint: disable=E1101
		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id) #pylint: disable=E1101

		if not user:
			return await msg.edit(content=f"<@!{ctx.author.id}>, failed to fetch your user data, try again later.") #pylint: disable=E1101

		data_parser = UserDataParser(user)
		await msg.edit(content="processing reward...")

		_type, _period, _prize = reward_data

		process_results = data_parser.process_user_rewards(reward_data, db.user_db)

		if process_results["eligible"]:
			if process_results["update_status"]:
				embed = discord.Embed(
					description=f"**{_type.capitalize()} Reward**",
					colour=embed_colour
				)

				embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url) #pylint: disable=E1101
				embed.add_field(name="Reward", value=f"**{_prize} Σ**", inline=True)
				embed.add_field(name="Next Reward", value=f"{process_results['next_reward']}", inline=True)
				return await msg.edit(content=None, embed=embed)

			return await msg.edit(content="Something went wrong while redeeming the reward...\nTry again later.")

		embed = discord.Embed(
			description=f"<@!{data_parser.get_id()[1]}>, you already collected this,\nplease wait `{process_results['next_reward']}`",
			colour=embed_colour
		)
		return await msg.edit(content=None, embed=embed)

class rewards(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def hourly(self, ctx):
		await RewardsCMDHandler.process_reward(ctx, (
			"hourly",
			60*60,
			random.randint(1, 20)
		))

	@hourly.error
	async def hourly_error(self, ctx, error):
		pass

	@commands.command()
	@commands.cooldown(1, 2, commands.BucketType.user) #pylint: disable=E1101
	async def daily(self, ctx):
		await RewardsCMDHandler.process_reward(ctx, (
			"daily",
			60*60*24,
			random.randint(1, 300)
		))

	@daily.error
	async def daily_error(self, ctx, error):
		pass

def setup(client):
	client.add_cog(rewards(client))