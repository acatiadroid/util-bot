import discord
from discord.ext import commands

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 818928333651050537:
            return

        try:
            message.content.isdecimal()
        except TypeError:
            await message.author.send('Incorrect number. Do `?count` to see the current number.')
            await message.delete()


        data = await self.bot.counter.find(723237557009252404)

        calc = data["count"] + 1

        if str(calc) != message.content:
            return await message.delete()

        currentnumber = data["count"] + 1

        await self.bot.counter.upsert(
            {
                "_id": 723237557009252404,
                "count": currentnumber
            }
        )
        await message.add_reaction('✅')

    @commands.command()
    async def count(self, ctx):
        data = await self.bot.counter.get_all()

        await ctx.send(f'We are currently at `{[str(d.get("count")) for d in data]}`')

    @commands.command()
    @commands.has_role('Moderator')
    async def cantcount(self, ctx, *, member:discord.Member):
        role = discord.utils.get(ctx.guild.roles, name = "Can't count")
        await member.add_roles(role)
        await ctx.send(f'**{member}** doesn\'t have the mental capacity to count, so they won\'t be able to anymore...')

def setup(bot):
    bot.add_cog(Counter(bot))

