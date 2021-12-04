import discord, asyncio
from discord.ext import commands
from configs.settings import embed_colour
from database.db import db
from parser.parsers import ItemData
from utils.items import *


class items_cmd(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def gift(self, ctx, receiver: discord.Member, amount=None, *, item_name=None):

		msg = await ctx.send("processing...")
		if not amount: return await msg.edit(content=f"Please specify the amount of items you want to gift!\nCheck `{ctx.prefix}help gift` for more info")
		try:
			amount = int(amount)
		except ValueError:
			if item_name == None:
				item_name = amount
			else:
				item_name = f"{amount} {item_name}"
			amount = 1

		sender = ctx.author
		if not item_name: return await msg.edit(content=f"Please specify the name of the item, try again\nCheck `{ctx.prefix}help gift` for more info")
		if receiver.bot: return await msg.edit(content=f"Seriously? You expect a bot to be registered in my database?")
		if sender.id == receiver.id: return await msg.edit(content="What\'s the point of gifting to yourself?\nStop wasting my resources!")
		if amount == 0: return await msg.edit(content="Scram! Stop wasting my resources to do a pointless task!")
		if amount < 0: return await msg.edit(content=f"You think you are funny?\nGifting negative items?")

		await msg.edit(content=f"checking item...")
		item = db.items_db.fetch_item_named(item_name, ctx.guild.id)
		if not item: return await msg.edit(content=f"`{item_name}` isn\'t an available item, try again later!\nCheck `{ctx.prefix}backpack` to see what you can gift!")
		item = ItemData(item)

		await msg.edit(content=f"processing data...")
		try: sender_amount_owned = item.get_amount_owned_by(sender.id)
		except KeyError: sender_amount_owned = 0
		try: receiver_amount_owned = item.get_amount_owned_by(receiver.id)
		except KeyError: receiver_amount_owned = 0
		max_amount = item.max_owned
		new_receiver_amount_owned = receiver_amount_owned + amount
		new_sender_amount_owned = sender_amount_owned - amount 

		if sender_amount_owned == 0: return await msg.edit(content=f"You don\'t even own any of that and you are trying to gift it")
		if receiver_amount_owned == max_amount: return await msg.edit(content="That user already owns the maximum amount of that item, you can\'t give them more")
		if amount > sender_amount_owned: return await msg.edit(content=f"You only have `{sender_amount_owned}` of `{item_name}`\nYou cannot possibly {ctx.invoked_with} `{amount}` of `{item_name}`")
		if new_receiver_amount_owned > max_amount: return await msg.edit(content=f"If you were to give that user `{amount}` of `{item_name}`,\nthey would exceed the maximum amount of `{item_name}` they can own")

		await msg.edit(content="processing gift...")

		update_fields, set_fields, unset_fields = {}, {}, {}
		if new_sender_amount_owned == 0: unset_fields[f"owners.{ctx.guild.id}-{sender.id}"] = 0
		else: set_fields[f"owners.{ctx.guild.id}-{sender.id}"] = new_sender_amount_owned
		set_fields[f"owners.{ctx.guild.id}-{receiver.id}"] = new_receiver_amount_owned
		if unset_fields != {}: update_fields["$unset"] = unset_fields
		update_fields["$set"] = set_fields

		update_result = item.update_fields(update_fields)
		success = bool(update_result.matched_count) and bool(update_result.modified_count)
		if not success: return await msg.edit(content=f"Something went wrong while processing the gift, try again later")
		
		embed = discord.Embed(
			description=f"You have sent `{amount}` of `{item_name}` to <@!{receiver.id}>!\n<@!{sender.id}>\'s `{item_name}` count: {new_sender_amount_owned}\n<@!{receiver.id}>\'s `{item_name}` count: {new_receiver_amount_owned}",
			colour=embed_colour
		)
		embed.set_author(name=f"Gift success")
		return await msg.edit(content=None, embed=embed)

	@gift.error
	async def gift_error(self, ctx, error):
		pass

	@commands.command(aliases=["purchase"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def buy(self, ctx, count=None, *, item_name=None):

		ctx.invoked_with = ctx.invoked_with.lower()
		msg = await ctx.send(content=f"processing...")
		if not count: return await msg.edit(content=f"Please specify the amount of items you want to {ctx.invoked_with}!\nCheck `{ctx.prefix}help {ctx.invoked_with}` for more info")
		try:
			count = int(count)
		except ValueError:
			if item_name == None:
				item_name = count
			else:
				item_name = f"{count} {item_name}"
			count = 1
		if count == 0: return await msg.edit(content=f"Come on! Don\'t try to waste my resources")
		if count < 0: return await msg.edit(content=f"How do you even {ctx.invoked_with} negative amounts of something")
		if not item_name: return await msg.edit(content=f"Please specify the name of the item, try again\nCheck `{ctx.prefix}help {ctx.invoked_with}` for more info")

		await msg.edit(content="fetching item and user...")
		item_data = db.items_db.fetch_item_named(item_name, ctx.guild.id)
		_does_not_exist_msg_ = f"`{ctx.prefix}shop`" if ctx.invoked_with in ["buy", "purchase"] else f"`{ctx.prefix}backpack`"
		if not item_data: return await msg.edit(content=f"`{item_name}` does not exist, check {_does_not_exist_msg_} for a list of items you can {ctx.invoked_with}")
		item = ItemData(item_data)

		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserData(user)
		user_id = user_parser.user_data['_id']

		await msg.edit(content=f"processing data...")
		try: amount_owned = item.get_amount_owned_by(ctx.author.id)
		except KeyError: amount_owned = 0

		try: supply = int(item.supply)
		except TypeError: supply = None

		max_amount = item.max_owned
		cumul_cost = item.get_cumul_cost_of(count)
		user_money = user_parser.get_user_money()

		new_item_count = amount_owned + count
		new_user_money = user_money - cumul_cost
		new_supply_count = None
		if supply == 0: return await msg.edit(content=f"No supply available")
		if supply and count > supply: return await msg.edit(content=f"There is only `{supply}` stock{'s' if supply > 1 else ''} of `{item_name}`\nYou cannot possibly {ctx.invoked_with} `{count}` of `{item_name}`\nThe maximum amount of `{item_name}` you can {ctx.invoked_with} is `{(supply - amount_owned) if ((supply - amount_owned) < (max_amount - amount_owned)) else (max_amount - amount_owned)}`")
		if amount_owned == max_amount: return await msg.edit(content=f"You already own the maximum amount of `{item_name}` which is `{max_amount}`")
		if new_item_count > max_amount: return await msg.edit(content=f"If you {ctx.invoked_with} `{count}` more of `{item_name}`, you will exceed the maximum amount of `{item_name}` you can own which is `{max_amount}`\nThe maximum amount of `{item_name}` you can {ctx.invoked_with} is `{max_amount-amount_owned}`")
		if cumul_cost > user_money: return await msg.edit(content=f"You can\'t afford `{count}` of `{item_name}` which costs **{cumul_cost:,} Σ**")
		if supply: new_supply_count = supply - count

		item_result = db.items_db.set_items_of(ctx.guild.id, user_id, item_name, new_item_count, new_supply_count)
		if not item_result['success']: return await msg.edit(content=f"Something went wrong while trying to update your items, try again later")

		money_result = user_parser.update_user_money(new_user_money)
		if not money_result: return await msg.edit(content=f"Something went wrong while trying to update your balance, try again later")

		embed = discord.Embed(
			title=f"Item{'s' if count > 1 else ''} Bought",
			description=f"You successfully bought `{count}` of `{item_name}` for **{cumul_cost:,} Σ**",
			colour=embed_colour
		)
		embed.add_field(name="New Balance", value=f"**{new_user_money:,} Σ**", inline=True)
		embed.add_field(name=f"Item{'s' if count > 1 else ''}", value=f"`{count}` `{item_name}`", inline=True)
		if supply: embed.add_field(name=f"New Item Supply", value=f"{new_supply_count}", inline=True)
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
		return await msg.edit(content=None, embed=embed)

	@buy.error
	async def buy_error(self, ctx, error):
		pass

	@commands.command(aliases=["refund"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def sell(self, ctx, count=None, *, item_name=None):

		ctx.invoked_with = ctx.invoked_with.lower()
		msg = await ctx.send(content=f"processing...")
		try:
			count = int(count)
		except ValueError:
			if item_name == None:
				item_name = count
			else:
				item_name = f"{count} {item_name}"
			count = 1
		if count == 0: return await msg.edit(content=f"Come on! Don\'t try to waste my resources")
		if count < 0: return await msg.edit(content=f"How do you even {ctx.invoked_with} negative amounts of something")
		if not item_name: return await msg.edit(content=f"Please specify the name of the item, try again\nCheck `{ctx.prefix}help {ctx.invoked_with}` for more info")

		await msg.edit(content="fetching item and user...")
		item_data = db.items_db.fetch_item_named(item_name, ctx.guild.id)
		_does_not_exist_msg_ = f"`{ctx.prefix}shop`" if ctx.invoked_with in ["buy", "purchase"] else f"`{ctx.prefix}backpack`"
		if not item_data: return await msg.edit(content=f"`{item_name}` does not exist, check {_does_not_exist_msg_} for a list of items you can {ctx.invoked_with}")
		item = ItemData(item_data)

		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserData(user)
		user_id = user_parser.user_data['_id']

		await msg.edit(content=f"processing data...")
		try: amount_owned = item.get_amount_owned_by(ctx.author.id)
		except KeyError: amount_owned = 0

		try: supply = int(item.supply)
		except TypeError: supply = None

		max_amount = item.max_owned
		user_money = user_parser.get_user_money()
		cumul_cost = round(item.get_cumul_cost_of(count) * 0.8)

		new_item_count = amount_owned - count
		new_user_money = user_money + cumul_cost
		new_supply_count = None
		if amount_owned < count: return await msg.edit(content=f"You only have `{amount_owned}` of `{item_name}`\nYou cannot possibly {ctx.invoked_with} `{count}` of `{item_name}`\nThe maximum amount of `{item_name}` you can {ctx.invoked_with} is `{amount_owned}`")
		if supply: new_supply_count = supply + count

		item_result = None
		if new_item_count == 0:
			item_result = db.items_db.remove_item_from_owner(ctx.guild.id, user_id, item_name, new_supply_count)
		else:
			item_result = db.items_db.set_items_of(ctx.guild.id, user_id, item_name, new_item_count, new_supply_count)
		if not item_result['success']: return await msg.edit(content=f"Something went wrong while trying to update your items, try again later")

		money_result = user_parser.update_user_money(new_user_money)
		if not money_result: return await msg.edit(content=f"Something went wrong while trying to update your balance, try again later")

		embed = discord.Embed(
			title=f"Item{'s' if count > 1 else ''} Sold",
			description=f"You successfully sold `{count}` of `{item_name}` for **{cumul_cost:,} Σ**",
			colour=embed_colour
		)
		embed.add_field(name="New Balance", value=f"**{new_user_money:,} Σ**", inline=True)
		embed.add_field(name=f"Item{'s' if count > 1 else ''}", value=f"`{count}` `{item_name}`", inline=True)
		if supply: embed.add_field(name=f"New Item Supply", value=f"{new_supply_count}", inline=True)
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
		return await msg.edit(content=None, embed=embed)

	@sell.error
	async def sell_error(self, ctx, error):
		pass

	@commands.command(aliases=["shop"])
	async def item(self, ctx, cmdtype=None, *, item_name=None):

		ctx.invoked_with = ctx.invoked_with.lower()
		msg = await ctx.send("fetching items...")
		if not cmdtype: cmdtype = "list"
		if not cmdtype.lower() in ["list", "info"]: return await msg.edit(content=f"`{cmdtype}` is none of the following:\n- `list`\n- `info`\ndo `{ctx.prefix}help {ctx.invoked_with}` for more info")

		items = db.items_db.fetch_items_of(ctx.guild.id)
		if not bool(len(items)): return await msg.edit(content=f"There are no items on this server, try again later")
		items = list(sorted(items, key=lambda item: item["cost"]))

		if cmdtype.lower() in ["list"]:

			return await paginated_menu_for_items(self, msg, ctx, items)

		await msg.edit(content=f"checking item...")
		if not item_name: return await msg.edit(content=f"Please specify the name of the item, try again")
		item_data = list(filter(lambda x: x if ((x["name"] == str(item_name)) and (x["server_id"] == str(ctx.guild.id))) else False, items))
		if not bool(len(item_data)): return await msg.edit(content=f"`{item_name}` does not exist, check `{ctx.prefix}{ctx.invoked_with} list` for a list of items")
		item_data = item_data[0]

		if cmdtype.lower() in ["info"]: return await msg.edit(content=None, embed=item_embed_content_of(ctx, item_data))
		return await msg.edit(content=f"You somehow broke the system!")

	@item.error
	async def item_error(self, ctx, error):
		pass

	@commands.command(aliases=["bp", "inventory", "inv"])
	async def backpack(self, ctx, member: discord.Member=None):
		ctx.invoked_with = ctx.invoked_with.lower()
		backpack, items = ("Inventory" if ctx.invoked_with in ["inv", "inventory"] else "Backpack"), None
		msg = await ctx.send("fetching items...")
		if member:
			if member.bot: return await msg.edit(content=f"Very funny, you know <@!{member.id}> is a bot.")
			items = db.items_db.fetch_user_items(f"{ctx.guild.id}-{member.id}")
			if not bool(len(items)): return await msg.edit(content=f"They appear to have nothing in their backpack!")
			items = list(sorted(items, key=lambda item: item["cost"]))
			context_for_member = CustomCommandContext(member, ctx.guild, ctx.message, ctx.author)
			return await paginated_menu_for_items(self, msg, context_for_member, items, backpack=backpack)

		items = db.items_db.fetch_user_items(f"{ctx.guild.id}-{ctx.author.id}")
		if not bool(len(items)): return await msg.edit(content=f"You appear to have nothing in your backpack!")
		items = list(sorted(items, key=lambda item: item["cost"]))
		return await paginated_menu_for_items(self, msg, ctx, items, backpack=backpack)

	@backpack.error
	async def backpack_error(self, ctx, error):
		pass

def setup(client):
	client.add_cog(items_cmd(client))