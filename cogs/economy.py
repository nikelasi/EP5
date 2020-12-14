import discord
from discord.ext import commands

class economy(commands.Cog):
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

def setup(client):
	client.add_cog(economy(client))
