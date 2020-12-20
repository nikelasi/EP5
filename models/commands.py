
help_cmd_struct = {
	("stat", "stats", "user", "bal"): {
		"description": "`{p}{cmd}`\nCheck your own stats\n\n`{p}{cmd} @User`\nChecks the stats of @User",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} @User")
		]
	},
	("leaderboard", "ldb", "lb"): {
		"description": "`{p}{cmd}`\nSee the leaderboard of the server!\nSorted according to **Σ**",
		"fields": []
	},
	("hourly"): {
		"description": "`{p}{cmd}`\nClaim **[1~20]** Σ per hour",
		"fields": []
	},
	("daily"): {
		"description": "`{p}{cmd}`\nClaim **[1~300]** Σ per day",
		"fields": []
	},
	("prefix"): {
		"description": "`{p}{cmd} <prefix>`\nSets my prefix to `<prefix>`\n[Requires Administrator]",
		"fields": [
			("Examples", "{p}{cmd} !\n{p}{cmd} e!")
		]
	},
	("ping"): {
		"description": "`{p}{cmd} <destination>`\nGets the latency of the respective destinations:\n- Bot > `bot`, `self`\n- Response Time > `response`, `time`, `reply`\n- Database > `db`, `mongo`, `database`",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} bot\n{p}{cmd} reply\n{p}{cmd} db")
		]
	},
	("help"): {
		"description": "`{p}{cmd}`\nGet a list of valid commands\n\n`{p}{cmd} <command>`\nGets info on <command>",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} ping\n{p}{cmd} stats")
		]
	},
	("pay", "send"): {
		"description": "`{p}{cmd} @User <amount>`\nPays @User **<amount> Σ**\n[1 execution per 2s cooldown]",
		"fields": [
			("Examples", "{p}{cmd} @User 100\n{p}{cmd} @User 20")
		]
	},
	("bank"): {
		"description": "`{p}{cmd}` info\nChecks your bank balance\n\n`{p}{cmd} withdraw <amount>`\nWithdraws <amount> from your bank balance\n\n`{p}{cmd} deposit <amount>`\nDeposits <amount> into your bank balance",
		"fields": [
			("Examples", "{p}{cmd} info\n{p}{cmd} withdraw 1000\n{p}{cmd} deposit 2500")
		]
	},
	("cf", "coinflip", "flip"): {
		"description": "`{p}{cmd}`\nFlips a coin and returns heads or tails\n\n`{p}{cmd} <Heads/Tails>`\nFlips a coin and tells you whether your guess was correct\n\n`{p}{cmd} <Heads/Tails> <bet>`\nFlips a coin and if your guess was correct, you will win the bet",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} Heads\n{p}{cmd} Tails 1000")
		]
	},
	("item", "shop"): {
		"description": "`{p}{cmd} list` or `{p}{cmd}`\nLists the items available\n\n`{p}{cmd} info <item-name>`\nReturns more info on <item-name>",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} list\n{p}{cmd} info Item")
		]
	},
	("sell", "refund"): {
		"description": "`{p}{cmd} <count> <item-name>`\nSells <count> of <item-name>, you only get a refund of 80%",
		"fields": [
			("Examples", "{p}{cmd} 1 Item\n{p}{cmd} 10 GreatItem"),
		]
	},
	("buy", "purchase"): {
		"description": "`{p}{cmd} <count> <item-name>`\nBuys <count> of <item-name>",
		"fields": [
			("Examples", "{p}{cmd} 1 Item\n{p}{cmd} 10 GreatItem"),
		]
	},
	("backpack", "bp", "inventory", "inv"): {
		"description": "`{p}{cmd}`\nCheck your backpack\n\n`{p}{cmd} @User`\nChecks the backpack of @User",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} @User")
		]
	}
}