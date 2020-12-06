import discord, asyncio, os, json, time
from discord.ext import commands
from function.db import get_prefix, set_prefix, db_ping
'''
import keep_alive
keep_alive.keep_alive()
'''

owner_ids = [593735027121061889, 348307478808756224]

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
	if message.content.strip() == "<@!784729572620894228>":
		await message.channel.send(
			f"My prefix is `{get_prefix(client, message)}`\ndo `{get_prefix(client, message)}help` for a list of commands!"
		)
	await client.process_commands(message)


@client.event
async def on_ready():
	print('FyreDiscord is dedn\'t')
	await client.change_presence(
		activity=discord.Activity(
			type=discord.ActivityType.watching, name="ҒΨRΣ"
		),
		status=discord.Status.online
	)


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(f'Invalid command, try `{ctx.prefix}help` for a list of commands.')
	elif isinstance(error, commands.MissingRequiredArgument):
		pass
	elif isinstance(error, discord.Forbidden):
		pass
	elif isinstance(commands.CheckFailure):
		pass
	elif "TimeoutError" in str(error):
		pass
	else:
		await ctx.send(f"Unexpected error occured\n\nCommand: `{ctx.message.content}`\n\nError: {error}")


@client.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, p):
	message = await ctx.send(f"Changing prefix to `{p}`...")
	set_prefix(ctx.message.guild.id, p)
	await message.edit(content=f"Prefix have been changed to `{p}`")

@client.command()
async def ping(ctx, destination=None):
	if destination in [None, "bot", "self"]:
		message = await ctx.send("Pinging...")
		await message.edit(content=f"Bot ping: `{round(client.latency * 1000)}ms`")
	elif destination in ["response", "reply", "time"]:
		before = time.monotonic()
		message = await ctx.send("Pong...")
		ping = (time.monotonic() - before)*1000
		await message.edit(content=f"Pong! `{round(ping)}ms`")
	elif destination in ["db", "mongo", "database"]:
		message = await ctx.send("Pinging database...")
		before = time.monotonic()
		db_ping()
		ping = (time.monotonic() - before)*1000
		await message.edit(content=f"Database ping: `{round(ping)}ms`")
	else:
		await ctx.send(f"`{destination}` isn\'t a valid destination to ping.\nYou can ping `bot`, `response` or `db`.")

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

@help.error
async def help_error(ctx, error):
	print(error)

@prefix.error
async def prefix_error(ctx, error):
	if isinstance(error, discord.Forbidden):
		await ctx.send("I don't have the necessary permissions to change my prefix")
	elif isinstance(error, commands.CheckFailure):
		await ctx.send("Sorry, you need to be an administrator to change my prefix")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"Please specify the prefix you want to set\nFor e.g. `{ctx.prefix}prefix !` will change my prefix to `!`")
	else:
		await ctx.send(f"Error: {error}")

@ping.error
async def ping_error(ctx, error):
	await ctx.send(f"Error: {error}")

for filename in os.listdir('./cogs'):
	if filename.endswith(".py"):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ['DISCORD_TOKEN'])
