import asyncio
from discord import Embed
from configs.settings import embed_colour
from database.db import db
from parser.parsers import UserData, ItemData

class CustomCommandContext:
	def __init__(self, author, guild, message, requester):
		self.author = author
		self.guild = guild
		self.message = message
		self.requester = requester

def item_embed_content_of(ctx, item_data, footer_info=None, backpack=None):
	item = ItemData(item_data)
	embed = Embed(
		title=item.name,
		description=item.description,
		colour=embed_colour
	)

	if not backpack: embed.set_author(icon_url=ctx.guild.icon_url, name=f"{ctx.guild.name}\'s Items")
	if backpack: embed.set_author(icon_url=ctx.author.display_avatar.url, name=f"{ctx.author}\'s {backpack}")
	embed.add_field(name="Cost", value=f"**{item_data['cost']:,} Σ**", inline=True)

	if f"{ctx.guild.id}-{ctx.author.id}" in item.owners_data:
		embed.add_field(name="Amount Owned", value=f"{item.get_amount_owned_by(ctx.author.id)}/{item.max_owned}", inline=True)
	else:
		embed.add_field(name="Amount Owned", value=f"0/{item.max_owned}", inline=True)

	if not backpack:
		if not item.supply:
			embed.add_field(name="Supply", value=f"Infinite", inline=True)
		else:
			embed.add_field(name="Supply", value=f"{item.supply} left", inline=True)

	embed.add_field(name="Base", value=f"**{item.average_price:,} Σ**", inline=True)
	embed.add_field(name="Min", value=f"{item.multipliers[0]}%", inline=True)
	embed.add_field(name="Max", value=f"{item.multipliers[1]}%", inline=True)
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