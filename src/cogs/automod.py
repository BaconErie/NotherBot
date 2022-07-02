# Automoderation tools for ChillBot
# Copyright 2022 StillChillDevs. See the LICENSE file to see full license

from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord import Option, Embed, Forbidden

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import storage


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create command groups
        self.pingspam = self.bot.create_group('pingspam', 'Automod for ping spam')
    
    ######################################
    # EVENT LISTENERS AND SLASH COMMANDS #
    ######################################

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        await self.check_spam_ping(message)

    # Muterole command
    @commands.slash_command(guild_ids=[992932470834069654])
    async def muterole(self, ctx,
        muterole: Option(discord.Role, 'The role to give to a muted person'),
        description='Set the server mute role'
    ):
        # Get the id of the muterole
        # Set that with the key 'muterole' in the guild storage
        # Confirm with the user that we have set the mute role
        # WE TRUST THAT DISCORD GAVE US A VALID ROLE

        storage.set_guild_data(ctx.guild.id, 'muterole', muterole.id)

        # Confirm with the user
        # Make the embed then send
        embed = Embed(color=0x05ff00)
        embed.add_field(name='Muterole Set', value=f'Successfully set {muterole.mention} as the muterole', inline=False)
        embed.set_footer(text='Make sure that the muterole actually works!')
        ctx.respond(embed=embed)
    
    # Mute command
    @commands.slash_command(guild_ids=[992932470834069654])



    # Ping Spam Slash Commands
    @commands.slash_command(guild_ids=[992932470834069654])
    async def set(self, ctx,
        limit: Option(int, 'The max amount of mentions per minute'),
        mute_duration: Option(int, 'Mute duration, IN MINUTES, if the person is muted for spam pinging'),
        pingspam = self.bot.create_group()
    ):
        self.pingspam

    #####################
    # PROCESS FUNCTIONS #
    #####################

    async def check_spam_ping(self, message):  
        '''Takes in the message and checks if the user is spam pinging'''

        # Goals:
        # 1. Check how many members were mentioned by this message, set that to members_mentioned
        # 2. Increment the amount of times the sender mentioned others in the last 60 seconds
        # 3. Check if the the sender mentioned people above the limit, if so mute them

        # Does the server even have spam ping detection on? If no, return
        # Does the message have mentions? If no, return
        if not storage.get_guild_data(message.guild.id, 'is_spam_ping_detect') or len(message.mentions) == 0:
            return

        # Goal 1: Check how many members were mentioned by this message, set that to members_mentioned
        members_mentioned = len(message.mentions)

        # Goal 2: Increment the amount of times the sender mentioned others in the last 60 seconds
        
        # First we have to get the mention_times list
        # mention_times contains the times when the member mentioned someone
        # For example, if the member mentioned 3 people at time x, then there will be 3 entries of x in mention_times
        # The time is in unix time in seconds
        # A mention_times is made for each user for each guild

        mention_times = storage.get_guild_user_data(message.guild.id, message.author.id, 'mention_times')

        # If the mention_times doesn't exist, make one and set it to blank for now
        if mention_times == None:
            storage.set_guild_user_data(message.guild.id, message.author.id, 'mention_times', [])
            mention_times = storage.get_guild_user_data(message.guild.id, message.author.id, 'mention_times')
        
        # Get the UTC unix time when the message was sent in seconds, then add the time to mention times
        # ... based on how many members was mentioned (members_mentioned)

        message_create_time = message.created_at.timestamp()

        print('Line 63, this is unix time at which message was created' + str(message_create_time))
        for x in range(members_mentioned):
            mention_times.append(message_create_time)
        
        # Goal 3: Check if the the sender mentioned people above the limit, if so mute them
        # First we need to get the mention_limit
        mention_limit = storage.get_guild_data(message.guild.id, 'mention_limit')

        if mention_limit == None:
            # Something is clearly wrong, for now just print to output
            print('Line 74, mention_limit does not exist, even though spam ping detection is on')

        mentions_in_last_minute = 0

        # Loop through mentions_times, and see which times are less than 60 seconds
        for time in mention_times:
            current_time = datetime.utcnow().timestamp()
            
            if current_time - time <= 60:
                # Mentioned in the last minute, increment mentions_in_last_minute
                mentions_in_last_minute += 1
            else:
                # Otherwise we can actually just remove the time from mention_times
                mention_times.remove(time)
        
        # Now we check if the mentions_in_last_minute is more than mention_limit
        if mentions_in_last_minute > mention_limit:
            # Mentions more than minute, get mute duration and mute the user
            mute_duration = storage.get_guild_data(message.guild.id, 'spam_ping_mute_duration')

            if mute_duration == None:
                # Something is clearly wrong, for now just print to output
                print('Line 95, mute_duration does not exist, even though spam ping detection is on')
            
            await self.mute(message.guild.id, message.member.id, self.bot.id, mute_duration, f'Mention spam: Member reached mentions per minute limit of {mention_limit}')
        
    async def mute(self, guild_id, member_id, moderator_id, duration, reason):
        '''Mutes a member in a given server for the specified amount of minutes, or forever if none'''
        
        # STEPS
        # 1. Check to see if the mute role is set, if not alert and return
        # 2. Check to make sure the mute role exists, if not alert and return
        # 3. Check to make sure the member exists, if not alert and return
        # 4. Check to make sure the moderator has manage role permission, if not alert and return
        # 5. Make sure duration is an integer, if not alert and return
        # 6. Try to add the role to the member, if there is a permission error alert and return
        # 7. If we are able to add the muted role, record it in the guild user storage

        muterole_id = storage.get_guild_data(guild_id, 'muterole')
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(member_id)
        moderator = guild.get_member(moderator_id)

        # Check if mute role is set
        if muterole_id == None:
            # If not return
            return 'mute role not set'
        
        muterole = guild.get_role(muterole_id)
        
        # Check if role exists
        if muterole == None:
            # If not return
            return 'mute role does not exist'
        
        # Check if the member exists
        if member == None:
            # If not return
            return 'member does not exist'

        # Check if the moderator has the manage role permission
        if not moderator.guild_permissions.manage_roles:
            # If no manage roles perm return
            return 'moderator does not have perms'
        
        # Make sure duration is an integer
        if type(duration) != int:
            return 'duration not an integer'
        
        # Try to add the role to the member
        try:
            await member.add_roles(muterole)
        except Forbidden:
            return 'no perms'
        
        # Record that the user is muted in the storage
        storage.set_guild_user_data(guild_id, member_id, 'is_muted', True)

        # Return with success
        return 'success'