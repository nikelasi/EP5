from discord import Embed
from configs.help_info import help_info_data
from configs.settings import embed_colour

def format_help_string(text, p, cmd):
	return text.replace('{p}', f'{p}').replace('{cmd}', f'{cmd}')

def get_cmd_data_for(cmd):

	cmd_data = None
	for aliases, data in help_info_data.items():
		cmd_data = (data, aliases) if cmd in aliases else None
		if cmd_data:
			return cmd_data
	return cmd_data
	
def get_help_embed_for(cmd, cmd_data, ctx):

	embed = Embed(
		title=f"**Command:** `{cmd}`",
		description=f"{format_help_string(cmd_data[0]['description'], ctx.prefix, cmd)}",
		colour=embed_colour
	)

	for name, value in cmd_data[0]["fields"]:
		embed.add_field(name=f"{format_help_string(name, ctx.prefix, cmd)}", value=f"{format_help_string(value, ctx.prefix, cmd)}", inline=True)

	if type(cmd_data[1]) != str:
		aliases = list(cmd_data[1])
		aliases.remove(cmd)
		aliases = map(lambda x: f"`{x}`", aliases)
		embed.add_field(name="Aliases", value=f"{' '.join(aliases)}", inline=True)

	return embed