import discord
from discord.ext import commands
import os
import asyncio
import json
'''
import keep_alive
keep_alive.keep_alive()
'''

owner_ids = [593735027121061889, 348307478808756224]


def get_prefix(client, message):
	prefixes = json.load(open("json/prefixes.json", 'r'))
	return prefixes.get(str(message.guild.id), prefixes['default'])

client = commands.Bot(command_prefix=get_prefix)
client.remove_command('help')


@client.command()
async def help(ctx):
	p = ctx.prefix
	embed = discord.Embed(
		description=f"no help lul",
		colour=discord.Colour.orange())

	embed.set_author(name="Help", icon_url=client.user.avatar_url)
	await ctx.send(embed=embed)


@client.event
async def on_message(message):
	if message.content.strip() == "<@!734352159684034570>":
		await message.channel.send(
			f"My prefix is `{get_prefix(client, message)}`\ndo `{get_prefix(client, message)}help` for a list of commands!"
		)
	await client.process_commands(message)


@client.event
async def on_ready():
	print('FyreDiscord is dedn\'t')
	await client.change_presence(
		activity=discord.Activity(
			type=discord.ActivityType.watching, name="ҒΨRΣ"),
			status=discord.Status.online
		)


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(f'Invalid command, try `{ctx.prefix}help` for a list of commands.')
	elif isinstance(error, commands.MissingRequiredArgument):
		pass
	elif "TimeoutError" in str(error):
		pass
	else:
		await ctx.send(f"Unexpected error occured\n\nCommand: `{ctx.message.content}`\n\nError: {error}")


@client.command()
async def prefix(ctx, p):
	prefixes = json.load(open("json/prefixes.json", 'r'))
	prefixes[str(ctx.message.guild.id)] = f"{p}"
	json.dump(prefixes, open("json/prefixes.json", "w"))
	await ctx.send(f"Prefix have been changed to `{p}`")


@client.command()
async def load(ctx, extension):
	if ctx.author.id in owner_ids:
		client.load_extension(f'cogs.{extension}')
		await ctx.send(f'Loaded {extension}')


@client.command()
async def unload(ctx, extension):
	if ctx.author.id in owner_ids:
		client.unload_extension(f'cogs.{extension}')
		await ctx.send(f'Unloaded {extension}')


@client.command()
async def reload(ctx, extension):
	if ctx.author.id in owner_ids:
		client.reload_extension(f'cogs.{extension}')
		await ctx.send(f'Reloaded {extension}')


@client.command()
async def ping(self, ctx):
	await ctx.send(f"{round(self.client.latency * 1000)} ms")

@help.error
async def help_error(ctx, error):
	print(error)


for filename in os.listdir('./cogs'):
	if filename.endswith(".py"):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ['DISCORD_TOKEN'])
