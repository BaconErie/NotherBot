# Automoderation tools for ChillBot
# Copyright 2022 BaconErie. See the LICENSE file to see full license

from datetime import datetime, timezone

import discord
from discord.ext import tasks, commands
from discord import Option, Embed, Forbidden

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import storage
from datetime import datetime, timezone

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create command groups
        self.pingspam = self.bot.create_group('pingspam', 'Automod for ping spam')

        # Start the unmute loop
        self.unmute_loop.start()

    ##############
    # LOOP THING #
    ##############

    @tasks.loop(minutes=1.0)
    async def unmute_loop(self):
        # STEPS
        # 1. Loop through all muted member_ids in muted_member_ids
        # 2. Check if the mute_end_time has passed. If so, unmute the user

        for guild in self.bot.guilds:
            mutelist = storage.get_guild_data(guild.id,'muted_member_ids')
            current_time = datetime.now(timezone.utc).timestamp()

            for entry in mutelist:
                if entry[1] < current_time and entry[1] != -1:
                    # If it's equal to -1, then its an indefinite mute
                    # Muted end time has passed, unmute

                    minutes_muted = int(int(current_time - entry[1])/60)

                    if minutes_muted == 0:
                        minutes_muted = 1
                    await self.unmute(guild.id, entry[0], self.bot.user.id, f'Automatic unmute after {minutes_muted} minutes')
        
    
    ######################################
    # EVENT LISTENERS AND SLASH COMMANDS #
    ######################################

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author == self.bot.user:
    #         return

    #     await self.check_spam_ping(message)

    # Muterole command
    @commands.slash_command(guild_ids=[992932470834069654], description='Set the server mute role')
    async def muterole(self, ctx,
        muterole: Option(discord.Role, 'The role to give to a muted person'),
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
        await ctx.respond(embed=embed)
    
    # Mute command
    @commands.slash_command(guild_ids=[992932470834069654], name='mute', description='Mutes a member for the specified amount of minutes, or forever if none')
    async def mute_user(self, ctx,
        user: Option(discord.User, 'User to mute'),
        duration: Option(int, 'Time in MINUTES to mute for. Leave blank to mute indefinitely', required=False),
        reason: Option(str, 'Optional reason to mute for.', required=False),
    ):
        status = await self.mute(ctx.guild.id, user.id, ctx.author.id, duration, reason)
        
        if status == 'mute role not set':
            await ctx.respond('You have not set a mute role yet! Set one up with the `/muterole` command!', ephemeral=True)

        elif status == 'mute role does not exist':
            await ctx.respond('A mute role was set, but does not exist anymore! Please try again with the `/muterole` command!', ephemeral=True)

        elif status == 'member does not exist':
            await ctx.respond('I cannot find the person to mute. Make sure that they haven\'t left the server already.', ephemeral=True)
        
        elif status == 'moderator does not have perms':
            await ctx.respond('You do not have permission to run this command. Make sure that you have the permission to manage roles.', ephemeral=True)

        elif status == 'duration not an integer':
            await ctx.respond('Make sure that duration is an integer that is above zero, or leave it blank', ephemeral=True)
        
        elif status == 'no perms':
            await ctx.respond('I do not have permission to mute the user! Make sure that my role is above the user\'s role, and that I have the "Manage Roles" permission.', ephemeral=True)
        
        elif status == 'success':
            if reason == None:
                if duration == None:
                    await ctx.respond(f'Sucessfully muted {user.mention} indefinitely. No reason is provided.')
                else:
                    await ctx.respond(f'Sucessfully muted {user.mention} for {duration} minutes. No reason is provided.')
            else:
                if duration == None:
                    await ctx.respond(f'Sucessfully muted {user.mention} indefinitely for reason: {reason}.')
                else:
                    await ctx.respond(f'Sucessfully muted {user.mention} for {duration} minutes. Reason: {reason}.')

    # Unmute command
    @commands.slash_command(guild_ids=[992932470834069654], name='unmute', description='Unmutes a member with an optional reason')
    async def unmute_user(self, ctx,
        user: Option(discord.User, 'User to unmute'),
        reason: Option(str, 'Reason for unmute', required=False),
    ):
        status = await self.unmute(ctx.guild.id, user.id, ctx.author.id, reason)

        if status == 'member does not exist':
            await ctx.respond('I cannot find the person to unmute. Make sure that they haven\'t left the server already.', ephemeral=True)
        
        elif status == 'muterole not found':
            await ctx.respond('You haven\'t set up a muterole yet, so I don\'t know which role to remove.', ephemeral=True)
        
        elif status == 'member not muted':
            await ctx.respond('I couldn\'t find the muterole in the member\'s role list, and so they are probably unmuted.', ephemeral=True)
        
        elif status == 'moderator does not have perms':
            await ctx.respond('You do not have permission to run this command. Make sure that you have the permission to manage roles.', ephemeral=True)
        
        elif status == 'no perms':
            await ctx.respond('I do not have permission to unmute the user! Make sure that my role is above the user\'s role, and that I have the "Manage Roles" permission.', ephemeral=True)
        
        elif status == 'success':
            if reason == None:
                await ctx.respond(f'Sucessfully unmuted {user.mention}. No reason was provided')
            else:
                await ctx.respond(f'Sucessfully unmuted {user.mention}. Reason: {reason}')

    @commands.slash_command(guild_ids=[992932470834069654], name='alertchannel', description='Sets the alert channel. THIS SHOULD BE SOMETHING LIKE A MOD CHAT!')
    async def alertchannel(self, ctx,
        alertchannel: Option(discord.TextChannel, 'Channel to log alerts. Leave blank to disable alert logging.')
    ):
        '''The alert channel is where urgent messages will be sent, for example reports or when a possible raider joins'''
        
        # STEPS:
        # 1. Check if the moderator has administrator permission, if not alert and return.
        # 2. Check if the alertchannel is none. If so 
        # 2. Check if the channel exists, if not alert and return.
        # 3. Check if the bot has send messages and embed permission in the GuildChannel. If not alert and return
        # 4. Get the alert channel id and store it
        # 5. Alert success

        # 1. Check if the moderator has administrator permission
        if not ctx.author.guild_permissions.administrator:
            ctx.respond('You must have administrator permission in order to set the alert channel!', ephemeral=True)
            return
        
        # 2. Check if the channel exists, if not alert and return
        alertchannel = ctx.guild.get_channel(alertchannel)
    
    # # Ping Spam Slash Commands
    # @commands.slash_command(guild_ids=[992932470834069654])
    # async def set(self, ctx,
    #     limit: Option(int, 'The max amount of mentions per minute'),
    #     mute_duration: Option(int, 'Mute duration, IN MINUTES, if the person is muted for spam pinging'),
    #     pingspam = self.bot.create_group()
    # ):
    #     self.pingspam
    

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
        # 5. Make sure duration is an integer and is above zero, if not alert and return
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
        
        # Make sure duration is an integer > 0 if not none
        if duration != None and (type(duration) != int or not duration > 0):
            return 'duration not an integer'
        
        # Try to add the role to the member
        try:
            if duration == None:
                if reason == None:
                    await member.add_roles(muterole, reason=f'Mute by moderator {moderator.name}#{moderator.discriminator} indefinitely. No reason provided.')
                else:
                    await member.add_roles(muterole, reason=f'Mute by moderator {moderator.name}#{moderator.discriminator} indefinitely. Reason: {reason}')
            else:
                if reason == None:
                    await member.add_roles(muterole, reason=f'Mute by moderator {moderator.name}#{moderator.discriminator} for {duration} minutes. No reason provided.')
                else:
                    await member.add_roles(muterole, reason=f'Mute by moderator {moderator.name}#{moderator.discriminator} for {duration} minutes. Reason: {reason}')
        except Forbidden:
            return 'no perms'
        
        # Record that the user is muted in the storage
        if duration == None:
            mute_end_time = -1
        else:
            mute_end_time = datetime.now(timezone.utc).timestamp() + duration * 60
        
        mute_list = storage.get_guild_data(guild_id, 'muted_member_ids')

        if mute_list == None:
            storage.set_guild_data(guild_id, 'muted_member_ids', [[member_id, mute_end_time]])
        else:
            mute_list.append([member_id, mute_end_time])
            storage.set_guild_data(guild_id, 'muted_member_ids', mute_list)

        # Return with success
        return 'success'
    
    async def unmute(self, guild_id, member_id, moderator_id, reason):
        '''Unmutes a member for the given reason'''

        # STEPS

        # CHECKS:
        # 1. Check if member exists, return 'member does not exist' if no
        # 2. Get the mute role, return 'muterole not found' if role does not exist
        # 3. Check if the member has the role, if not return 'member not muted'
        # 4. Check if the moderator has manage roles permission, if not return 'moderator does not have perms'

        # MAIN STEPS
        # 5. Try to remove the mute role from the user, return 'no perms' if Forbidden exception
        # 6. Record in storage that the user is no longer muted
        # 7. Return success if we reached here

        # 1. Check if the member exists, if not return 'member does not exist'
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(member_id)
        moderator = guild.get_member(moderator_id)

        if member == None:
            return 'member does not exist'

        # 2. Get the mute role, return 'muterole not found' if role does not exist
        muterole_id = storage.get_guild_data(guild_id, 'muterole')

        if muterole_id == None:
            return 'muterole not found'
        
        muterole = guild.get_role(muterole_id)
        if muterole == None:
            return 'muterole not found'
        
        # 3. Check if the member has the role, if not return 'member not muted'
        if muterole not in member.roles:
            return 'member not muted'
        
        # 4. Check if the moderator has manage roles permission, if not return 'moderator does not have perms'
        if not moderator.guild_permissions.manage_roles:
            return 'moderator does not have perms'
        
        # 5. Try to remove the mute role from the user, return 'no perms' if Forbidden exception
        try:
            if reason == None:
                await member.remove_roles(muterole, reason=f'Unmute by moderator {moderator.name}#{moderator.discriminator}. No reason provided.')
            else:
                await member.remove_roles(muterole, reason=f'Unmute by moderator {moderator.name}#{moderator.discriminator}. Reason: {reason}.')
        except Forbidden:
            return 'no perms'
        
        # 6. Record in storage that the user is no longer muted
        mute_list = storage.get_guild_data(guild_id, 'muted_member_ids')

        for entry in mute_list:
            if entry[0] == member_id:
                mute_list.remove(entry)
                storage.set_guild_data(guild_id, 'muted_member_ids', mute_list)

        # 7. Return success if we reached here
        return 'success'

    ####################
    # HELPER FUNCTIONS #
    ####################

    def can_alert(self, guild):
        '''Checks if the alert channel in that guild exists, and makes sure the bot can chat in that channel'''
        pass

def setup(bot):
    bot.add_cog(AutoMod(bot))