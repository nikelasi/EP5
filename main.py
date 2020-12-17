import os, json, time, asyncio #pylint: disable=W0611
import discord
from discord.ext import commands
from models.db import db
from models.commands import help_cmd_struct
from models.constants import embed_colour

owner_ids = [593735027121061889, 348307478808756224]
in_development = True

client = commands.Bot(command_prefix=db.prefix_db.get_prefix, case_insensitive=True)
client.remove_command('help')

def format_help_string(text, p, cmd):
	return text.replace('{p}', f'{p}').replace('{cmd}', f'{cmd}')

@client.command()
async def help(ctx, cmd=None):
	msg = await ctx.send(f"fetching command data...")
	if cmd:
		cmd = cmd.lower()
		cmd_data = None

		for aliases, data in help_cmd_struct.items():
			cmd_data = (data, aliases) if cmd in aliases else None
			if cmd_data: break
		if not cmd_data: return await msg.edit(content=f"Command `{cmd}` does not exist!")

		embed = discord.Embed(
			title=f"**Command:** `{cmd}`",
			description=f"{format_help_string(cmd_data[0]['description'], ctx.prefix, cmd)}",
			colour=embed_colour
		)

		for name, value in cmd_data[0]["fields"]:
			embed.add_field(name=f"{format_help_string(name, ctx.prefix, cmd)}", value=f"{format_help_string(value, ctx.prefix, cmd)}", inline=True)

		if type(cmd_data[1]) != str:
			aliases = list(cmd_data[1])
			aliases.remove(cmd)
			aliases = map(lambda x: f"`{x}`", aliases)
			embed.add_field(name="Aliases", value=f"{' '.join(aliases)}", inline=True)

		return await msg.edit(content=None, embed=embed)

	embed = discord.Embed(
		title=f"**Commands**",
		description=f"Need more help? Run **`{ctx.prefix}help <command>`** to get info on a command!",
		colour=embed_colour
	)

	#embed.set_author(name="Commands", icon_url=client.user.avatar_url)
	embed.add_field(name="User", value=f"`stats`, `leaderboard`", inline=True)
	embed.add_field(name="Economy", value=f"`pay`", inline=True)
	embed.add_field(name="Rewards", value=f"`hourly`, `daily`", inline=True)
	embed.add_field(name="System", value=f"`ping`, `prefix`, `help`", inline=True)
	return await msg.edit(content=None, embed=embed)

@client.event
async def on_message(message):
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
	elif isinstance(error, commands.CheckFailure):
		pass
	elif isinstance(error, commands.CommandOnCooldown):
		embed = discord.Embed(
			description=f"That command is on {str(error.cooldown.type).split('.')[-1]} cooldown,\ntry again in `{error.retry_after:,.2f}s!`",
			colour=embed_colour
		)
		await ctx.send(embed=embed)
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
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"Setting random 11-digit long prefix...\nGIVE ME A PREFIX GENIUS\nExample:`{ctx.prefix}prefix !` will change my prefix to `!`")

@ping.error
async def ping_error(ctx, error):
	pass

for filename in os.listdir('./cogs'):
	if filename.endswith(".py"):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ['DISCORD_TOKEN'])
