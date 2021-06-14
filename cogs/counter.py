import discord
from discord.ext import commands

from utils.secrets import GUILD_ID, COUNTING_CHANNEL


class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != COUNTING_CHANNEL:
            return

        print('1')

        try:
            message.content.isdecimal()
        except TypeError:
            await message.author.send('Incorrect number. Do `?count` to see the current number.')
            await message.delete()

        data = await self.bot.counter.find(GUILD_ID)
        if not data:
            await self.bot.counter.upsert({"_id": GUILD_ID, "count": 1})

        calc = data["count"] + 1

        if str(calc) != message.content:
            return await message.delete()

        currentnumber = data["count"] + 1

        await self.bot.counter.upsert(
            {
                "_id": GUILD_ID,
                "count": currentnumber
            }
        )
        await message.add_reaction('✅')

    @commands.command()
    async def count(self, ctx):
        data = await self.bot.counter.find(GUILD_ID)

        await ctx.send(f'We are currently at {data["count"]}')

    @commands.command()
    @commands.has_role('Moderator')
    async def cantcount(self, ctx, *, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Can't count")
        await member.add_roles(role)
        await ctx.send(f'**{member}** doesn\'t have the mental capacity to count, so they won\'t be able to anymore...')


def setup(bot):
    bot.add_cog(Counter(bot))
