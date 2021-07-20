import os, json, time, asyncio, random, threading, discord
from discord.ext import commands, tasks
from utils.main import *
from configs.settings import embed_colour
from database.db import db
from utils.formatters import seconds_to_time

owner_ids = [593735027121061889, 348307478808756224]
in_development = False

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=db.prefix_db.get_prefix, case_insensitive=True, intents=intents)
client.remove_command('help')

class PriceUpdateData:
	def __init__(self, guilds):
		self.last_updated = None
		self.__update__data__(guilds)

	def __update__data__(self, guilds):
		self.guilds = guilds
		self.guilds_data = []
		messages_info = db.message_info_db.fetch_all()
		for guild, webhooks in self.guilds:
			guild_id = guild.id
			msgs_info = list(filter(lambda info: info['server_id'] == str(guild_id), messages_info))
			self.guilds_data.append({"guild": guild, "id": guild_id, "info": msgs_info, "webhooks": webhooks})

P_U_D = None

@client.command()
async def help(ctx, cmd=None):
	msg = await ctx.send(f"fetching command data...")
	if cmd:
		cmd = cmd.lower()
		cmd_data = get_cmd_data_for(cmd)
		if not cmd_data: return await msg.edit(content=f"Command `{cmd}` does not exist!")
		return await msg.edit(content=None, embed=get_help_embed_for(cmd, cmd_data, ctx))

	embed = discord.Embed(
		title=f"**Commands**",
		description=f"Need more help? Run **`{ctx.prefix}help <command>`** to get info on a command!",
		colour=embed_colour
	)

	#embed.set_author(name="Commands", icon_url=client.user.avatar_url)
	embed.add_field(name="User", value=f"`stats`, `leaderboard`", inline=True)
	embed.add_field(name="Economy", value=f"`pay`, `bank`", inline=True)
	embed.add_field(name="Items", value=f"`backpack`, `shop`, `buy`, `sell`, `sc`, `gift`", inline=True)
	embed.add_field(name="Rewards", value=f"`hourly`, `daily`", inline=True)
	embed.add_field(name="Fun", value=f"`coinflip`, `dice`, `would_you_rather`", inline=True)
	embed.add_field(name="Others", value=f"`collections`", inline=True)
	embed.add_field(name="System", value=f"`ping`, `prefix`, `help`", inline=True)
	return await msg.edit(content=None, embed=embed)

@client.event
async def on_message(message):
	if isinstance(message.channel, discord.DMChannel):
		return
	if message.author.bot:
		return

	if in_development and message.channel.id not in [673402525969547285]:
		return


	if message.content.strip() == "<@!784729572620894228>":
		await message.channel.send(
			f"My prefix is `{db.prefix_db.get_prefix(client, message)}`\ndo `{db.prefix_db.get_prefix(client, message)}help` for a list of commands!"
		)

	if f"{message.guild.id}-{message.author.id}" not in db.users:
		success = db.user_db.create_user(message.author.id, message.guild.id)

	await client.process_commands(message)

@tasks.loop(minutes=15.0)
async def price_update_loop():
	global P_U_D
	P_U_D.__update__data__([(guild, await guild.webhooks()) for guild in client.guilds])
	P_U_D.last_updated = time.time()
	await asyncio.gather(*[db.items_db.update_items_price(guild_data=guild_data) for guild_data in P_U_D.guilds_data])

'''@tasks.loop(seconds=30.0)
async def MM_Loop():
	global MM_MSG
	MM_TIMESTAMP = 1618183800
	time_to_mm = round(MM_TIMESTAMP - int(time.time()))
	formatted_time = seconds_to_time(time_to_mm)
	msg = f"`{formatted_time}` to <@!348307478808756224>'s Motivational Monday Presentation!"
	channel = client.get_channel(761058088358248458)
	if MM_MSG is None:
		MM_MSG = await channel.send(msg)
	else:
		await MM_MSG.edit(content=msg)'''

@client.event
async def on_ready():
	global P_U_D
	P_U_D = PriceUpdateData([(guild, await guild.webhooks()) for guild in client.guilds])
	P_U_D.last_updated = time.time()
	price_update_loop.start()
	print("Price Update Data Loop started")
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
		ctx.invoked_with = ctx.invoked_with.lower()
		stat_cmd, bp_cmd = ["stats", "user", "bal", "stat"], ["bp", "inventory", "inv", "backpack"]
		ignored_cases = stat_cmd + bp_cmd
		if ctx.invoked_with in ignored_cases: return
		await ctx.send(f"You did not pass in required arguments\n here\'s some info and examples on `{ctx.invoked_with}`")
		await ctx.send(embed=get_help_embed_for(ctx.invoked_with, get_cmd_data_for(ctx.invoked_with), ctx))

	elif isinstance(error, discord.Forbidden):
		pass
	elif isinstance(error, commands.CheckFailure):
		pass
	elif isinstance(error, commands.CommandOnCooldown):
		embed = discord.Embed(
			description=f"That command is on {str(error.cooldown.type).split('.')[-1]} cooldown,\ntry again in `{error.retry_after:,.2f}s!`",
			colour=embed_colour
		)
		await ctx.send(embed=embed)
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send(f"Hilarious, that person does not exist in discord.")
	elif isinstance(error, commands.UnexpectedQuoteError):
		await ctx.send(f"If you want to include a quote, you must quote the whole thing\nFor eg. `NJ's Coding Skills bad` will be `\"NJ's Coding Skills bad\"`")
	elif "TimeoutError" in str(error):
		pass
	else:
		await ctx.send(f"{error}")
		raise error

@client.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, p):
	message = await ctx.send(f"Changing prefix to `{p}`...")
	db.prefix_db.set_prefix(ctx.message.guild.id, p)
	await message.edit(content=f"Prefix have been changed to `{p}`")

@client.command(aliases=["stock_change", "pc", "price_change"])
async def sc(ctx):
	global P_U_D
	msg = await ctx.send(f"checking time...")
	last_updated = round(P_U_D.last_updated)
	next_updated = last_updated + 60*15
	time_to_update = round(next_updated - int(time.time()))
	formatted_time = seconds_to_time(time_to_update)
	return await msg.edit(content=f"`{formatted_time}` to next price change")

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
		_ = db.db_ping()
		ping = (time.monotonic() - before)*1000
		await message.edit(content=f"Database ping: `{round(ping)}ms`")
	else:
		await ctx.send(f"`{destination}` isn\'t a valid destination to ping.\nYou can ping `bot`, `response` or `db`.")

@client.command()
async def reload_iul(ctx):
	if ctx.author.id in owner_ids:
		global P_U_D
		msg = await ctx.send('reloading...')
		P_U_D.__update__data__([(guild, await guild.webhooks()) for guild in client.guilds])
		await msg.edit(content=f'Updated Data for `Price Update Data`')

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
	pass

@prefix.error
async def prefix_error(ctx, error):
	if isinstance(error, discord.Forbidden):
		await ctx.send("I require permission. I am not allowed to change my prefix yet so...")
	elif isinstance(error, commands.CheckFailure):
		await ctx.send("You appear to be unqualified or not have the permission.\nYou need to be admin to change my prefix")

@ping.error
async def ping_error(ctx, error):
	pass

for filename in os.listdir('./cogs'):
	if filename.endswith(".py") and filename != "__init__.py":
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ['DISCORD_TOKEN'])
