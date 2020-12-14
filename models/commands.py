
help_cmd_struct = {
	("stat", "stats", "user", "bal"): {
		"description": "`{p}{cmd}`\nCheck your own stats\n\n`{p}{cmd} @User`\nChecks the stats of @User",
		"fields": [
			("Examples", "{p}{cmd}\n{p}{cmd} @User")
		]
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
	}
}