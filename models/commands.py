
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
			("Examples", "{p}{cmd} info\n{p}{cmd} wiithdraw 1000\n{p}{cmd} deposit 2500")
		]
	}
}