import discord
from discord.ext import commands

import os
import re
# import json
from discord.commands import Option

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, owner_ids=[727548572542959754])

bot.load_extension('cogs.automod')

@bot.event
async def on_ready():
    print('NotherBot connected and ready.')

bot.run()