import discord
from discord.ext import commands
from models.db import db
from models.constants import embed_colour
import asyncio


def frame_embed_content_of(ctx, frame_data, footer_info=None):
	embed = discord.Embed(
		title=frame_data["_id"],
		description=f"{frame_data['description']}\nrun `{ctx.prefix}{ctx.invoked_with.lower()} info {frame_data['_id']}` to view",
		colour=embed_colour
	)

	embed.set_author(name=f"Collections")
	embed.add_field(name="Frames", value=f"**{len(list(frame_data['links']))} Σ**", inline=True)

	if footer_info:
		frame_no, frames_no = footer_info
		embed.set_footer(text=f"Collection {frame_no} of {frames_no} | Requested by {ctx.author}")

	return embed

def link_frame_embed_content_of(ctx, collection_name, frame_link, footer_info=None):
	embed = discord.Embed(
		title=collection_name,
		colour=embed_colour
	)

	embed.set_image(url=frame_link)

	if footer_info:
		frame_no, frames_no = footer_info
		embed.set_footer(text=f"Frame {frame_no} of {frames_no} | Requested by {ctx.author}")

	return embed

class others(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["frame", "collection", "collections", "col"])
	async def frames(self, ctx, cmdtype=None, *, frame_name=None):
		db_key = "frames"
		frames_db = db.database[db_key]
		ctx.invoked_with = ctx.invoked_with.lower()
		msg = await ctx.send("fetching frames...")
		if not cmdtype: cmdtype = "list"
		if not cmdtype.lower() in ["list", "view"]: return await msg.edit(content=f"`{cmdtype}` is none of the following:\n- `list`\n- `view`\ndo `{ctx.prefix}help {ctx.invoked_with}` for more info")

		frames = list(frames_db.find({}))
		if not bool(len(frames)): return await msg.edit(content=f"There are no collections of frames available, try again later")

		if cmdtype.lower() in ["list"]:
			frames_count = len(frames)
			cur_frame_no = 1

			await msg.edit(content=None, embed=frame_embed_content_of(ctx, frames[cur_frame_no-1], (cur_frame_no, frames_count)))

			reactions = ["⏮️", "◀️", "▶️", "⏭️"]
			for reaction in reactions: await msg.add_reaction(reaction)

			def check(reaction, user):
				return user == ctx.author and reaction.message.id == msg.id

			while True:
				try:
					reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)

					if str(reaction.emoji) == "▶️" and cur_frame_no != frames_count:
						cur_frame_no += 1

					elif str(reaction.emoji) == "◀️" and cur_frame_no > 1:
						cur_frame_no -= 1

					elif str(reaction.emoji) == "⏮️":
						cur_frame_no = 1

					elif str(reaction.emoji) == "⏭️":
						cur_frame_no = frames_count

					if str(reaction.emoji) in reactions:
						await msg.edit(content=None, embed=frame_embed_content_of(ctx, frames[cur_frame_no-1], (cur_frame_no, frames_count)))
					await msg.remove_reaction(reaction, user)

				except asyncio.TimeoutError:
					await msg.clear_reactions()
					break
			return

		await msg.edit(content=f"checking item...")
		if not frame_name: return await msg.edit(content=f"Please specify the name of the frame, try again")
		frame_data = list(filter(lambda x: x if (x["_id"] == str(frame_name)) else False, frames))
		if not bool(len(frame_data)): return await msg.edit(content=f"`{frame_name}` collection does not exist, check `{ctx.prefix}{ctx.invoked_with} list` for a list of collections")
		frame_data = frame_data[0]

		if cmdtype.lower() in ["view"]:
			links = list(frame_data['links'])
			frames_count = len(links)
			cur_frame_no = 1

			await msg.edit(content=None, embed=link_frame_embed_content_of(ctx, frame_data['_id'], links[cur_frame_no-1], (cur_frame_no, frames_count)))

			reactions = ["⏮️", "◀️", "▶️", "⏭️"]
			for reaction in reactions: await msg.add_reaction(reaction)

			def check(reaction, user):
				return user == ctx.author and reaction.message.id == msg.id

			while True:
				try:
					reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)

					if str(reaction.emoji) == "▶️" and cur_frame_no != frames_count:
						cur_frame_no += 1

					elif str(reaction.emoji) == "◀️" and cur_frame_no > 1:
						cur_frame_no -= 1

					elif str(reaction.emoji) == "⏮️":
						cur_frame_no = 1

					elif str(reaction.emoji) == "⏭️":
						cur_frame_no = frames_count

					if str(reaction.emoji) in reactions:
						await msg.edit(content=None, embed=link_frame_embed_content_of(ctx, frame_data['_id'], links[cur_frame_no-1], (cur_frame_no, frames_count)))
					await msg.remove_reaction(reaction, user)

				except asyncio.TimeoutError:
					await msg.clear_reactions()
					break
			return
		return await msg.edit(content=f"You somehow broke the system!")

	@frames.error
	async def frames_error(self, ctx, error):
		pass

def setup(client):
	client.add_cog(others(client))