from configs.settings import embed_colour
from discord import Embed

def frame_embed_content_of(ctx, frame_data, footer_info=None):
	embed = Embed(
		title=frame_data["_id"],
		description=f"{frame_data['description']}\nrun `{ctx.prefix}{ctx.invoked_with.lower()} info {frame_data['_id']}` to view",
		colour=embed_colour
	)

	embed.set_author(name=f"Collections")
	embed.add_field(name="Frames", value=f"**{len(list(frame_data['links']))}**", inline=True)

	if footer_info:
		frame_no, frames_no = footer_info
		embed.set_footer(text=f"Collection {frame_no} of {frames_no} | Requested by {ctx.author}")

	return embed

def link_frame_embed_content_of(ctx, collection_name, frame_link, footer_info=None):
	embed = Embed(
		title=collection_name,
		colour=embed_colour
	)

	embed.set_image(url=frame_link)

	if footer_info:
		frame_no, frames_no = footer_info
		embed.set_footer(text=f"Frame {frame_no} of {frames_no} | Requested by {ctx.author}")

	return embed