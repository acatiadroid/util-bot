import discord
import requests
import re
import datetime
import asyncio
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from copy import deepcopy
from discord.ext import commands, tasks

from utils.secrets import MUTE_ROLE_ID, GUILD_ID, ADDBOT_BLACKLIST_ROLE, ADMIN_CHANNEL, HIDE_NSFW_ROLE_ID, MOD_ROLE_NAME

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @tasks.loop(seconds=3)
    async def check_reminders(self):
        currentTime = datetime.datetime.now()
        reminders = deepcopy(self.bot.reminders)
        for key, value in reminders.items():

            reminderTime = value['setAt'] + \
                relativedelta(seconds=value['duration'])

            if currentTime >= reminderTime:
                guild = self.bot.get_guild(GUILD_ID)
                channel = guild.get_channel(value['channelId'])
                message = channel.fetch_message(value['messageId'])

                await message.reply(f'This is a reminder for **{value["reason"]}**.')
                await self.bot.reminders.delete(value["_id"])

    @tasks.loop(seconds=30)
    async def check_selfmutes(self):
        currentTime = datetime.datetime.now()
        selfmutes = deepcopy(self.bot.selfmute)
        for key, value in selfmutes.items():

            muteTime = value['setAt'] + \
                relativedelta(seconds=value['duration'])

            if currentTime >= muteTime:
                guild = self.bot.get_guild(GUILD_ID)
                member = guild.get_member(value["_id"])
                role = await guild.get_role(MUTE_ROLE_ID)
                if role not in member.roles:
                    return

                await member.remove_roles(role)

                await self.bot.selfmute.delete(member.id)

    @commands.command(aliases=['rm', 'reminder'])
    async def remind(self, ctx, time: TimeConverter, reason: commands.clean_content = None):
        if reason == None:
            reason = 'something'

        await self.bot.reminders.upsert(
            {
                "_id": ctx.author.id,
                "duration": time,
                "setAt": datetime.datetime.now(),
                "messageId": ctx.message.id,
                "channelId": ctx.channel.id,
                "reason": str(reason)
            }
        )

        length = "{}".format(str(timedelta(seconds=time)))

        await ctx.send(f':ok_hand: Alright, I\'ll remind you in {length} for **{reason}**')

        if time < 300:
            await asyncio.sleep(time)

            await ctx.message.reply(f'This is a reminder for **{reason}**.')

            await self.bot.reminders.delete(ctx.author.id)

    @commands.command()
    async def selfmute(self, ctx, time: TimeConverter):
        """Lets you mute yourself for a set duration of time. Cannot be longer than 24 hours. Do not ask mods to unmute you."""

        if time > 86400:
            return await ctx.send('Cannot be longer than 24 hours.')

        if time < 300:
            return await ctx.send('Cannot be shorter than 5 minutes.')

        await self.bot.selfmute.upsert(
            {
                "_id": ctx.author.id,
                "duration": time,
                "setAt": datetime.datetime.now()
            }
        )
        try:
            muterole = ctx.guild.get_role(MUTE_ROLE_ID)
            await ctx.author.add_roles(muterole, reason='Self-mute')
            length = "{}".format(str(timedelta(seconds=time)))
            await ctx.send(
                f':ok_hand: Muted for **{length}**. Be sure not to bother anyone about it.')
            await ctx.author.send('You have muted yourself. Please do not contact mods to unmute you.')

            if time < 300:
                await asyncio.sleep(time)
                await ctx.author.remove_roles(muterole, reason='Self-mute expired.')
                await self.bot.selfmute.delete(ctx.author.id)

        except Exception as e:
            print(e)

    @commands.command()
    async def afk(self, ctx, *, note: commands.clean_content = None):
        """Marks you as AFK, so when you get mentioned, it will inform the user that you're AFK."""
        if note == None:
            note = 'No note set.'
        currentname = ctx.author.display_name
        try:
            await self.bot.afk.upsert(
                {
                    "_id": ctx.author.id,
                    "nick": str(currentname),
                    "reason": str(note)
                }
            )

            try:
                await ctx.author.edit(nick=f'[AFK] {currentname}')
            except:
                pass
            await ctx.send(f'You are now AFK, **{ctx.author}**. Say anything to untoggle this!')
        except Exception as e:
            await ctx.send('Failed to set you as AFK: ```{}```'.format(e))

    @commands.command()
    async def source(self, ctx):
        """Gets the source code for this bot on GitHub."""
        await ctx.send('Utilities#2289 source code: <https://github.com/acatiadroid/util-bot>')

    @commands.command()
    async def addbot(self, ctx, *, content: commands.clean_content):
        """
        Put your bot invite URL and a short list of what your bot does in the content field. This allows you to have you bot added to the server.
        """
        bannedrole = ctx.guild.get_role(ADDBOT_BLACKLIST_ROLE)
        if bannedrole in ctx.author.roles:
            return await ctx.send('You are banned from adding bots.')
        await ctx.send(
            'Your bot submission has been sent and is awaiting approval from Admins.\n\nIn the mean time, please do `?tag addbotrules` to see our rules on adding bots. We will DM you once (if) your bot gets added.')
        await ctx.message.delete()
        ch = discord.utils.get(ctx.guild.channels, id=ADMIN_CHANNEL)
        embed = discord.Embed(title='Bot request', description=content)
        embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
        embed.set_footer(text=f'Bot owner ID: {ctx.author.id}')
        await ch.send(embed=embed)

    @commands.command()
    @commands.has_role('Admin')
    async def acceptbot(self, ctx, botname: str, member: discord.Member):
        await member.send(
            f'👍 Your bot **{botname}** was added to ISgood community by {ctx.author.mention}.\n\nYour bot has access to <#808139553797308426>, <#808140224659062834>, the Music voice channels and a few other hidden channels. It also only has basic permissions, such as `Read Messages` and `Send Messages`. Check `?tag addbotrules` to make sure your bot doesn\'t get removed.')
        await ctx.send('Done.')

    @commands.group(invoke_without_command=True)
    async def docs(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs>')

    @docs.command(aliases=['moderation'])
    async def mod(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#moderation-commands>')

    @docs.command()
    async def links(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#useful-links>')

    @docs.command(aliases=['config'])
    async def configuration(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#configuration>')

    @docs.command(aliases=['misc'])
    async def miscellaneous(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#miscellaneous>')

    @docs.command(name='embed', aliases=['embeds'])
    async def embed_cmd(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#custom-embeds>')

    @docs.command()
    async def role(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#role-management>')

    @docs.command()
    async def info(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#information-commands>')

    @docs.command()
    async def suggestions(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#suggestions>')

    @docs.command(aliases=['star'])
    async def starboard(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#starboard>')

    @docs.command()
    async def tickets(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#tickets>')

    @docs.command()
    async def purge(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#purge>')

    @docs.command(name='logging', aliases=['log'])
    async def _logging(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#logging>')

    @docs.command(name='snowflake')
    async def snow_flake(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#snowflakes>')

    @commands.command()
    @commands.has_role('Moderator')
    async def ignorebot(self, ctx, *, id: int):
        await self.bot.botactivity.upsert(
            {
                "_id": id
            }
        )
        await ctx.send(':ok_hand: I will now ignore that bot.')

    @commands.command()
    async def hidensfw(self, ctx):
        """Toggles your visiblity between channels marked as NSFW."""
        role = ctx.guild.get_role(HIDE_NSFW_ROLE_ID)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send(':ok_hand: NSFW channels has been unhidden.')
        else:
            await ctx.author.add_roles(role)
            await ctx.send(
                ':ok_hand: NSFW channels have been hidden.\nDo the same command to unhide the NSFW channels.')

    @commands.command()
    async def raw(self, ctx, messageid: int, channel: discord.TextChannel = None):
        """Shows the raw unformatted content of a message."""
        if not channel:
            channel = ctx.channel

        try:
            msg = await channel.fetch_message(messageid)
        except discord.NotFound:
            return await ctx.send('Message not found')
        finally:
            await ctx.send(f'`{msg.author}` said:\n```{msg.content}```')

    @commands.command()
    async def cat(self, ctx):
        """Sends images and GIFs of cats"""
        try:
            api = requests.get(
                'https://api.thecatapi.com/v1/images/search').json()
            await ctx.send(api[0]["url"])
        except Exception as e:
            print(e)

    @commands.command()
    async def dog(self, ctx):
        """Sends images and GIFs of dogs"""
        api = requests.get('https://dog.ceo/api/breeds/image/random').json()
        await ctx.send(api["message"])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Autorole"""
        if member.guild.id != GUILD_ID:
            return

        if not member.bot:
            return

        roles = [808136380647080027]

        for role in roles:
            try:
                role = member.guild.get_role(role)
                await member.add_roles(role)
            except:
                print('Something broke with autorole')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        muterole = member.guild.get_role(MUTE_ROLE_ID)
        if muterole in member.roles:
            await self.bot.stickymute.upsert({"_id": member.id})

    @commands.command()
    @commands.has_role(MOD_ROLE_NAME)
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        """Bans a member. Mod-only of course."""
        await member.ban(reason=f'Banned by {ctx.author}: {reason}')
        await ctx.send(':ok_hand:')


def setup(bot):
    bot.add_cog(Random(bot))
