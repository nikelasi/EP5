import random, discord
from discord.ext import commands
from utils.rewards import process_reward


class rewards(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def hourly(self, ctx):
		await process_reward(ctx, (
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
		await process_reward(ctx, (
			"daily",
			60*60*24,
			random.randint(1, 300)
		))

	@daily.error
	async def daily_error(self, ctx, error):
		pass

def setup(client):
	client.add_cog(rewards(client))