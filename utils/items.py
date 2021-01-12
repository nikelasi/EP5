import asyncio
from discord import Embed
from configs.settings import embed_colour
from database.db import db
from parser.parsers import UserData

class CustomCommandContext:
	def __init__(self, author, guild, message, requester):
		self.author = author
		self.guild = guild
		self.message = message
		self.requester = requester

async def shop_transactions_check(ctx, msg, count, item_name):
	ctx.invoked_with = ctx.invoked_with.lower()
	if not count: return f"Please specify the amount of items you want to {ctx.invoked_with}!\nCheck `{ctx.prefix}help {ctx.invoked_with}` for more info"
	try:
		count = int(count)
	except ValueError:
		if item_name == None:
			item_name = count
		else:
			item_name = f"{count} {item_name}"
		count = 1
	if count == 0: return f"Come on! Don\'t try to waste my resources"
	if count < 0: return f"How do you even {ctx.invoked_with} negative amounts of something"
	if not item_name: return f"Please specify the name of the item, try again\nCheck `{ctx.prefix}help {ctx.invoked_with}` for more info"

	await msg.edit(content="fetching item and user...")
	item_data = db.items_db.fetch_item_named(item_name, ctx.guild.id)
	_does_not_exist_msg_ = f"`{ctx.prefix}shop`" if ctx.invoked_with in ["buy", "purchase"] else f"`{ctx.prefix}backpack`"
	if not item_data: return f"`{item_name}` does not exist, check {_does_not_exist_msg_} for a list of items you can {ctx.invoked_with}"

	user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
	if not user: return f"Hmm... somehow you don\'t exist to me, try again later!"
	user_parser = UserData(user)
	user_id = user_parser.user_data['_id']

	await msg.edit(content=f"processing data...")
	try:
		amount_owned = item_data["owners"][f"{user_id}"]
	except KeyError:
		amount_owned = 0

	try:
		supply = int(item_data["supply"])
	except TypeError:
		supply = None

	max_amount = item_data["max"]
	item_cost = item_data["cost"]
	cumul_cost = item_cost*count
	user_money = user_parser.get_user_money()

	return count, item_name, item_data, user, user_parser, user_id, amount_owned, supply, max_amount, item_cost, cumul_cost, user_money

def item_embed_content_of(ctx, item_data, footer_info=None, backpack=None):
	embed = Embed(
		title=item_data["name"],
		description=item_data["description"],
		colour=embed_colour
	)

	if not backpack: embed.set_author(icon_url=ctx.guild.icon_url, name=f"{ctx.guild.name}\'s Items")
	if backpack: embed.set_author(icon_url=ctx.author.avatar_url, name=f"{ctx.author}\'s {backpack}")
	embed.add_field(name="Cost", value=f"**{item_data['cost']:,} Σ**", inline=True)

	if f"{ctx.guild.id}-{ctx.author.id}" in item_data["owners"]:
		embed.add_field(name="Amount Owned", value=f"{item_data['owners'][f'{ctx.guild.id}-{ctx.author.id}']}/{item_data['max']}", inline=True)
	else:
		embed.add_field(name="Amount Owned", value=f"0/{item_data['max']}", inline=True)

	if not backpack:
		if not item_data['supply']:
			embed.add_field(name="Supply", value=f"Infinite", inline=True)
		else:
			embed.add_field(name="Supply", value=f"{item_data['supply']} left", inline=True)

	embed.add_field(name="Base", value=f"**{item_data['avg_price']:,} Σ**", inline=True)
	embed.add_field(name="Min", value=f"{item_data['multipliers'][0]}%", inline=True)
	embed.add_field(name="Max", value=f"{item_data['multipliers'][1]}%", inline=True)
	if footer_info:
		item_no, items_no = footer_info
		if type(ctx) is CustomCommandContext: embed.set_footer(text=f"Item {item_no} of {items_no} | Requested by {ctx.requester}")
		else: embed.set_footer(text=f"Item {item_no} of {items_no} | Requested by {ctx.author}")

	return embed

async def paginated_menu_for_items(self, msg, ctx, items, backpack=None):
	items_count = len(items)
	cur_item_no = 1
	if backpack:
		await msg.edit(content=None, embed=item_embed_content_of(ctx, items[cur_item_no-1], (cur_item_no, items_count), backpack))
	else:
		await msg.edit(content=None, embed=item_embed_content_of(ctx, items[cur_item_no-1], (cur_item_no, items_count)))

	reactions = ["⏮️", "◀️", "▶️", "⏭️"]
	for reaction in reactions: await msg.add_reaction(reaction)

	check = None

	if type(ctx) is CustomCommandContext:
		def check(reaction, user):
			return user == ctx.requester and reaction.message.id == msg.id
	else:
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == msg.id

	while True:
		try:
			reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)

			if str(reaction.emoji) == "▶️" and cur_item_no != items_count:
				cur_item_no += 1

			elif str(reaction.emoji) == "◀️" and cur_item_no > 1:
				cur_item_no -= 1

			elif str(reaction.emoji) == "⏮️":
				cur_item_no = 1

			elif str(reaction.emoji) == "⏭️":
				cur_item_no = items_count

			if str(reaction.emoji) in reactions:
				if backpack:
					await msg.edit(content=None, embed=item_embed_content_of(ctx, items[cur_item_no-1], (cur_item_no, items_count), backpack))
				else:
					await msg.edit(content=None, embed=item_embed_content_of(ctx, items[cur_item_no-1], (cur_item_no, items_count)))
			await msg.remove_reaction(reaction, user)

		except asyncio.TimeoutError:
			await msg.clear_reactions()
			break
	return