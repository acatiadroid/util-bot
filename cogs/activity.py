import discord
from datetime import datetime
from discord.ext import commands

from utils.secrets import BOT_STATUS_CHANNEL, GUILD_ID

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot and not after.bot:
            return

        aadata = await self.bot.botactivity.find(before.id)
        
        if before.guild.id != GUILD_ID:
            return

        x = ["online", "dnd", "idle"]

        logchannel = discord.utils.get(before.guild.channels, id = BOT_STATUS_CHANNEL)
        if str(before.status) in x and str(after.status) == "offline":
            await self.bot.botstatus.upsert({"_id":before.id, "down":datetime.utcnow()})
            if aadata:
                return
            await logchannel.send(f'<:offline:805576352450871346> {before.mention} (**{before}**) is offline. `[{datetime.utcnow().strftime("%m/%d/%Y, at %I:%M:%S %p")} UTC]`')

        if str(before.status) == "offline" and str(after.status) in x:
            data = await self.bot.botstatus.find(before.id)
            if not data:
                downtime = "Couldn't track when the bot went offline."
            else:
                try:
                    downtime = datetime.utcnow() - data["down"]
                except Exception as e:
                    await logchannel.send(e)
                hours, remainder = divmod(int(downtime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)
                await self.bot.botstatus.upsert(
                    {
                        "_id":before.id,
                        "uptime": datetime.utcnow()
                    }
                )
                downtime = f"{days}d {hours}h {minutes}m {seconds}s"
            if aadata:
                return
            await logchannel.send(f'<:online:805576670353948702> {before.mention} (**{before}**) is now online. `[{downtime}]`')
            try:
                await self.bot.botstatus.delete_by_id(before.id)
            except:
                pass


def setup(bot):
    bot.add_cog(Activity(bot))