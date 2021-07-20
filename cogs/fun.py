import random, enum, discord, requests, asyncio, json, difflib, time
from discord.ext import commands
from configs.settings import embed_colour
from database.db import db
from parser.parsers import UserData
from bs4 import BeautifulSoup

class Coinflip(enum.Enum):
	HEADS = "Heads"
	TAILS = "Tails"

class WYR_Answers(enum.Enum):
	RED = "🟥"
	BLUE = "🟦"

class fun(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(aliases=["flip", "cf"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def coinflip(self, ctx, heads_or_tails=None, bet=None):

		try:
			bet = int(bet)
			if bet == 0: bet = None
			if bet < 0: return await ctx.send(content=f"No no, you think I forgot about checking whether the bet is negative?")
		except ValueError:
			if bet != None: return await ctx.send(content=f"What does betting `{bet}` even mean? Does `{bet}` look like an integer to you?")
		except TypeError: pass

		msg = await ctx.send("flipping coin...")
		probability = random.randrange(452, 558+1)
		tails_percentage, heads_percentage, heads_threshold = f"{100 - (probability/10)}%", f"{probability/10}%", probability/1000
		coinflip_result = random.random()
		result = Coinflip.HEADS
		if coinflip_result > heads_threshold:
			result = Coinflip.TAILS

		embed = discord.Embed(
			description=f"{tails_percentage} of flipping tails\n{heads_percentage} of flipping heads",
			colour=embed_colour
		)
		embed.set_author(name="Coinflip")
		embed.add_field(name="Result", value=result.value, inline=True)
		
		if not heads_or_tails and not bet: return await msg.edit(content=None, embed=embed)
		await msg.edit(content="doing checks...")

		if not heads_or_tails.capitalize() in [possibility.value for possibility in Coinflip]: return await msg.edit(content=f"`{heads_or_tails.capitalize()}` is neither any of the following: {', '.join(map(lambda x: f'`{x}`', [result.value for result in Coinflip]))}")
		guess = {True: "correct", False: "wrong"}.get(heads_or_tails.capitalize() == result.value)
		embed.description = f"{embed.description}\nYour guess was {guess}!"
		embed.add_field(name="Guess", value=heads_or_tails.capitalize(), inline=True)
		if not bet: return await msg.edit(content=None, embed=embed)

		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserData(user)
		user_balance = user_parser.get_user_money()

		if user_balance < bet: return await msg.edit(content=f"Your user balance is **{user_balance:,} Σ**!\nYou cannot possibly bet more than you have!")

		new_balance, win_indicator = {"correct": (user_balance+bet, f"\nYou won **{bet:,} Σ**"), "wrong": (user_balance-bet, f"\nYou lost **{bet:,} Σ**")}.get(guess)
		success = {
			"correct": user_parser.update_user_money(new_balance),
			"wrong": user_parser.update_user_money(new_balance)
		}.get(guess)

		embed.description += win_indicator
		embed.add_field(name="Balance", value=f"**{new_balance:,} Σ**", inline=True)
		return await msg.edit(content=None, embed=embed)

	@coinflip.error
	async def coinflip_error(self, ctx, error):
		pass

	@commands.command(aliases=["roll", "die"])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def dice(self, ctx, guess=None, bet=None):

		try:
			bet = int(bet)
			if bet == 0: bet = None
			if bet < 0: return await ctx.send(content=f"No no, you think I forgot about checking whether the bet is negative?")
		except ValueError:
			if bet != None: return await ctx.send(content=f"What does betting `{bet}` even mean? Does `{bet}` look like an integer to you?")
		except TypeError: pass

		msg = await ctx.send("rolling dice...")
		result = random.randint(1, 6)

		embed = discord.Embed(
			description=f"1 in 6 chance for rolling any number",
			colour=embed_colour
		)
		embed.set_author(name="Dice")
		embed.add_field(name="Result", value=f"**{result}**", inline=True)
		
		if not guess and not bet: return await msg.edit(content=None, embed=embed)
		await msg.edit(content="doing checks...")

		try: guess = int(guess)
		except ValueError: return await msg.edit(content=f"Your guess, `{guess}`, isn\'t a number at all, this is merely a standard dice where you can choose 1 to 6")
		if not (guess in range(1, 6+1)): return await msg.edit(content=f"Your guess, `{guess}`, is not within 1 to 6, I\'m sure you know how a standard dice work")
		user_correct = {True: "correct", False: "wrong"}.get(guess == result)
		embed.description = f"{embed.description}\nYour guess was {user_correct}!"
		embed.add_field(name="Guess", value=f"**{guess}**", inline=True)
		if not bet: return await msg.edit(content=None, embed=embed)

		user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
		if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
		user_parser = UserData(user)
		user_balance = user_parser.get_user_money()

		if user_balance < bet: return await msg.edit(content=f"Your user balance is **{user_balance:,} Σ**!\nYou cannot possibly bet more than you have!")

		new_balance, win_indicator = {"correct": (user_balance+bet, f"\nYou won **{bet:,} Σ**"), "wrong": (user_balance-bet, f"\nYou lost **{bet:,} Σ**")}.get(user_correct)
		success = {
			"correct": user_parser.update_user_money(new_balance),
			"wrong": user_parser.update_user_money(new_balance)
		}.get(guess)

		embed.description += win_indicator
		embed.add_field(name="Balance", value=f"**{new_balance:,} Σ**", inline=True)
		return await msg.edit(content=None, embed=embed)

	@dice.error
	async def dice_error(self, ctx, error):
		pass

	@commands.command(aliases=['wyr'])
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def would_you_rather(self, ctx):

		msg = await ctx.send("fetching question...")

		# START SCRAPE #
		result = requests.get("http://either.io/")
		src = result.content
		soup = BeautifulSoup(src, 'html.parser')

		containers = soup.findAll("div", {"class":"result"})[2:4]

		blue_option = containers[0].findAll("span", {"class":"option-text"})[0].text
		red_option = containers[1].findAll("span", {"class":"option-text"})[0].text
		blue_count = int(containers[0].findAll("span", {"class","count"})[0].text.replace(",", ""))
		red_count = int(containers[1].findAll("span", {"class","count"})[0].text.replace(",", ""))

		more_info = soup.find("p", {"class": "more-info"}).text
		if len(more_info) == 0: more_info = "No info"
		#  END  SCRAPE #

		answer = None
		if blue_count > red_count: answer = WYR_Answers.BLUE
		elif blue_count < red_count: answer = WYR_Answers.RED
		else: return await ctx.send(f"{ctx.author.name}, please try again.\nThere was no correct answer for the Would You Rather question.")

		await msg.edit(content=f"formatting question...")
		embed = discord.Embed(
			title = f"Would You Rather",
			description = f"<@!{ctx.author.id}>, guess which one most people chose.\n🟦 {blue_option}\n\n🟥 {red_option}\n\nReact with 🟦 or 🟥 to choose\n\nReact with 🇽 to cancel",
			colour = embed_colour
		)

		embed.add_field(name="More Info", value=f"{more_info}")
		embed.set_author(name=f'{ctx.author}', icon_url=ctx.author.avatar_url)
		await msg.edit(content=None, embed=embed)
		reactions = ["🟦", "🟥", "🇽"]
		for reaction in reactions: await msg.add_reaction(reaction)
		chosen = None
		def check(reaction, user):
			return user == ctx.author and reaction.message.id == msg.id

		while True:
			try:
				reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
				if str(reaction.emoji) == "🟦": chosen = WYR_Answers.BLUE
				elif str(reaction.emoji) == "🟥": chosen = WYR_Answers.RED
				elif str(reaction.emoji) == "🇽":
					await msg.clear_reactions()
					return await msg.edit(content=f"Question has been terminated", embed=None)
				if str(reaction.emoji) in ["🟦", "🟥"]: break
				await msg.remove_reaction(reaction, user)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
				return await msg.edit(content=f"{ctx.author} has taken too long to respond, question has been terminated.", embed=None)

		await msg.clear_reactions()

		embed = discord.Embed(
			title = f"Would You Rather",
			description = f"🟦 {blue_option}: {blue_count:,}\n\n🟥 {red_option}: {red_count:,}\n",
			colour = embed_colour
		)
		embed.add_field(name="Answer", value=f"{answer.value}", inline=True)
		embed.add_field(name="Guess", value=f"{chosen.value}", inline=True)
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
		if chosen == answer:
			money = random.randint(25, 50)
			user = db.user_db.fetch_user(ctx.author.id, ctx.guild.id)
			if not user: return await msg.edit(content=f"Hmm... somehow you don\'t exist to me, try again later!")
			user_parser = UserData(user)
			user_balance = user_parser.get_user_money()
			new_balance = user_balance + money

			update_success = user_parser.update_user_money(new_balance)
			if not update_success: return await msg.edit(content=f"Something went wrong while crediting your account, try again later", embed=None)

			embed.description = f"{embed.description}\nYou were correct! You earned **{money} Σ**"
			embed.add_field(name="Balance", value=f"**{new_balance:,} Σ**")
		else:
			embed.description = f"{embed.description}\nYou were wrong! Better luck next time!"

		return await msg.edit(content=None, embed=embed)

	@would_you_rather.error
	async def would_you_rather_error(self, ctx, error):
		pass

	@commands.command(aliases=["tr", "type_racer", "typerace"])
	async def typeracer(self, ctx):

		msg = await ctx.send("generating a sentence...")
		sentence_list = json.loads(
			requests.get(
				"https://randomwordgenerator.com/json/sentences.json"
			).content
		)["data"]
		sentence = random.choice(sentence_list)["sentence"]

		embed = discord.Embed(
			title=f"TypeRacer ({ctx.author.name})",
			description=f"When ▶️ is pressed, a countdown from 3 to 1 will begin.\nWhen the countdown ends, a sentence will be displayed, and you have to type it out and send it as quick as you can!\n\nPress ▶️ to start countdown",
			colour=embed_colour
		)
		await msg.edit(content=None, embed=embed)
		await msg.add_reaction("▶️")
		check = lambda reaction, user: user == ctx.author and reaction.message.id == msg.id

		while True:
			try:
				reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
				if str(reaction.emoji) == "▶️": break
				await msg.delete_reaction(reaction, user)
			except asyncio.TimeoutError:
				return await msg.edit(content="Timed Out: You took too long to respond", embed=None)
		await msg.clear_reactions()

		embed = discord.Embed(
			title=f"TypeRacer ({ctx.author.name})",
			colour=embed_colour
		)

		for num in [":three:", ":two:", ":one:"]:
			embed.add_field(name="Countdown", value=num)
			await msg.edit(content=None, embed=embed)
			await asyncio.sleep(1)
			embed.remove_field(0)

		user_sentence = ""
		time_elapsed = 0.0
		embed.description = f"Type the following sentence!"
		embed.add_field(name="Sentence", value=f"`{sentence}`")
		await msg.edit(content=None, embed=embed)
		check = lambda message: message.author == ctx.author and ctx.channel.id == message.channel.id
		try:
			start = time.time()
			message = await self.client.wait_for('message', timeout=120, check=check)
			time_elapsed += time.time() - start
			user_sentence += message.content
			await message.delete()
			embed.add_field(name="Your Sentence", value=f"`{user_sentence.strip()}`")
			await msg.edit(content=None, embed=embed)
		except asyncio.TimeoutError:
			return await msg.edit(content="Timed Out: You left the race idle.", embed=None)

		await msg.edit(content="Finished. Calculating...", embed=None)

		user_sentence = user_sentence.strip()
		char_typed = len(user_sentence)
		cps = round(char_typed/time_elapsed)
		accuracy = (difflib.SequenceMatcher(None, sentence, user_sentence).ratio()*100)
		raw_wpm = round((char_typed/5)/(time_elapsed/60))
		wpm = round(raw_wpm*(accuracy/100))
		if len(user_sentence) > len(sentence)+15 or raw_wpm > 240:
			embed.description = f"__**Results**__\n||no u joker, u know what u did||"
			return await msg.edit(content=None, embed=embed)
		embed.description = f"__**Results**__\nTime Taken: {time_elapsed:.1f}s\nCharacters Per Second (CPS): **{cps}**\nWords Per Minute (WPM): **{wpm if wpm < 125 else str(wpm) + ' (likely copy pasted)'}**\nRaw WPM: **{raw_wpm}**\nAccuracy: **{accuracy:.1f}%**"
		return await msg.edit(content=None, embed=embed)

	@typeracer.error
	async def typeracer_error(self, ctx, error):
		print(error)



	#@commands.command(aliases=["chal", "ch"])
	#async def challenge(self, ctx, member:discord.Member=None, game_mode=None, bet=None):
	#	ctx.invoked_with = ctx.invoked_with.lower()
	#	msg = await ctx.send("processing...")
	#	if not member: return await msg.edit(content=f"Please specify who you want to challenge!\ndo `{ctx.prefix}help {ctx.invoked_with}` for more info")
	#	if not game_mode: return await msg.edit(content=f"Please specify the game mode you want to challenge {member.name} on")
	#	try:
	#		bet = int(bet)
	#		if bet < 0: return await msg.edit(content="you can\' bet negative amount of money")
	#		if bet == 0: bet = None
	#	except ValueError:
	#		if bet != None: return await msg.edit(content=f"Does {bet} look like a number to you?")
	#	except TypeError: pass
	#
	#	game_modes, game_mode = ["coinflip", "dice"], game_mode.lower()
	#	if not game_mode in game_modes: return await msg.edit(content=f"Please select an available gamemode!\nAvailable gamemodes are:\n{', '.join(map(lambda x: f'`{x}`', game_modes))}\ntry again")
	#
	#	game_function = {
	#		"coinflip": func,
	#		"dice": func
	#	}.get(game_mode)
	#
	#@challenge.error
	#async def challenge_error(self, ctx, error):
	#	pass

def setup(client):
	client.add_cog(fun(client))