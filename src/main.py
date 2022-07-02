import config

import discord
from discord.ext import commands

import os
import re
# import json
from discord.commands import Option

intents = discord.Intents.all()
bot = discord.Bot(intents=intents, owner_ids=config.OWNER_IDS)


@bot.slash_command(name='flag')
async def report_command(
    ctx, 
    link: Option(str, 'Enter the link of the offending message'), 
    reason: Option(str, 'Enter the reason why you flagged the message (e.g. give rule broken)')
):

    guild_id = ctx.guild.id
    flagged_message_id = re.search(r"([^\/]+$)", link).group()

    flag_data_raw = open('flag.json', 'w+')

    flag_data = json.loads(flag_data_raw.read())

    #Check if message has already been flagged
    if guild_id in flag_data.keys():
        if flagged_message_id = None #havent finished this command yet

for file in os.listdir('cogs'):
    if file.endswith('.py'):
        bot.load_extension('cogs.' + file[:-3])

bot.run(config.TOKEN)