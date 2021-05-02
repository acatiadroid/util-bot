import discord
import requests, json
from discord.ext import commands


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def afk(self, ctx, *, note: commands.clean_content=None):
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
        bannedrole = ctx.guild.get_role(808134855744684042)
        if bannedrole in ctx.author.roles:
            return await ctx.send('You are banned from adding bots.')
        await ctx.send(
            'Your bot submission has been sent and is awaiting approval from Admins.\n\nIn the mean time, please do `?tag addbotrules` to see our rules on adding bots. We will DM you once (if) your bot gets added.')
        await ctx.message.delete()
        ch = discord.utils.get(ctx.guild.channels, id=728304518173032449)
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
        await ctx.send('<https://acatiadroid.github.io/docs/#miscellaneous>')

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
    async def music(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#music>')

    @docs.command()
    async def rr(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#reaction-roles>')

    @docs.command()
    async def tickets(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#tickets>')

    @docs.command()
    async def purge(self, ctx):
        await ctx.send('<https://acatiadroid.github.io/docs/#purge>')

    @commands.command()
    @commands.has_role('Moderator')
    async def ignorebot(self, ctx, *, id: int):
        await self.bot.botactivity.upsert(
            {
                "_id": id
            }
        )
        await ctx.send('I will now ignore that bot. :ok_hand:')

    @commands.command()
    async def hidensfw(self, ctx):
        """Toggles your visiblity between channels marked as NSFW."""
        role = ctx.guild.get_role(820088043146313799)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send('NSFW channels has been unhidden. :ok_hand:')
        else:
            await ctx.author.add_roles(role)
            await ctx.send(
                'NSFW channels have been hidden. :ok_hand:\nDo the same command to unhide the NSFW channels.')

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
            api = requests.get('https://api.thecatapi.com/v1/images/search').json()
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
        if member.guild.id != 723237557009252404:
            return

        if not member.bot:
            return
        muterole = member.guild.get_role(797534434354135040)
        logchannel = member.guild.get_channel(800806829264470017)
        roles = [808136380647080027, 808129797905186857, 808129440327794699, 808129441573896203, 808129645261881344]
        mutedata = await self.bot.stickymute.find(member.id)

        for role in roles:
            try:
                role = member.guild.get_role(role)
                await member.add_roles(role)
            except:
                print('Something broke with autorole')

        if not mutedata:
            return

        await member.add_roles(muterole)
        await logchannel.send(f'Automatically muted **{member}** ({member.id}) for leaving and rejoining whilst muted.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        muterole = member.guild.get_role(797534434354135040)
        if muterole in member.roles:
            await self.bot.stickymute.upsert({"_id": member.id})



def setup(bot):
    bot.add_cog(Random(bot))