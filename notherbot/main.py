import discord
from discord.ext import commands

import os
import re
# import json
from discord.commands import Option

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, owner_ids=[727548572542959754])

bot.load_extension('cogs.automod')

bot.run('OTkyOTM4MTM2NDIwMjI5MjIx.GpwT3T.LEjreE3VzT8P4u-RqFGUDpbk2W6icQOMAGUdxM')