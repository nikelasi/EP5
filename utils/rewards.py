import time
from discord import Embed
from configs.settings import embed_colour
from .formatters import seconds_to_time
from parser.parsers import UserData
from database.db import db

def process_user_rewards(user_data, reward_details):

	_type, _period, _prize = reward_details
	now = int(time.time())
	last_collected = user_data.rewards_data[_type]
	timeframe = now-last_collected

	multiplier = 1
	if user_data.get_prestige() != 0:
		multiplier += (0.75*(user_data.get_prestige()))
	_prize = round(_prize * multiplier)

	if timeframe // _period > 0: #eligible for rewards
		new_amount = user_data.user_data["money"] + _prize
		success = db.user_db.update_user_set_fields(
			{"_id": user_data.user_data["_id"]},
			[
				(f"rewards.{_type}", now),
				(f"money", new_amount)
			]
		)

		return {
			"eligible": True,
			"update_status": success,
			"prize": _prize,
			"next_reward": seconds_to_time(_period)
		}

	next_collection_time = last_collected + _period
	time_to_collection = next_collection_time - now

	return {
		"eligible": False,
		"next_reward": seconds_to_time(time_to_collection)
	}

async def process_reward(ctx, reward_data): #pylint: disable=E0213

	msg = await ctx.send(f"fetching your user data...") #pylint: disable=E1101
	user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id) #pylint: disable=E1101

	if not user:
		return await msg.edit(content=f"<@!{ctx.author.id}>, failed to fetch your user data, try again later.") #pylint: disable=E1101

	data_parser = UserData(user)
	await msg.edit(content="processing reward...")

	_type, _period, _prize = reward_data

	process_results = process_user_rewards(data_parser, reward_data)

	if process_results["eligible"]:
		if process_results["update_status"]:
			_prize = process_results["prize"]
			embed = Embed(
				description=f"**{_type.capitalize()} Reward**",
				colour=embed_colour
			)

			embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url) #pylint: disable=E1101
			embed.add_field(name="Reward", value=f"**{_prize} Σ**", inline=True)
			embed.add_field(name="Next Reward", value=f"{process_results['next_reward']}", inline=True)
			return await msg.edit(content=None, embed=embed)

		return await msg.edit(content="Something went wrong while redeeming the reward...\nTry again later.")

	embed = Embed(
		description=f"<@!{data_parser.get_id()[1]}>, you already collected this,\nplease wait `{process_results['next_reward']}`",
		colour=embed_colour
	)
	return await msg.edit(content=None, embed=embed)