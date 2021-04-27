import discord
import os
import motor.motor_asyncio
from pathlib import Path
from discord.ext import commands

import utils.json_loader
from utils.mongo import Document
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = commands.when_mentioned_or('?'), case_insensitive=True, intents=intents)

bot.help_command = commands.MinimalHelpCommand()

cwd = Path(__file__).parents[0]
cwd = str(cwd)
bot.cwd = cwd
secret_file = utils.json_loader.read_json("secrets")
bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="?help • ISgood Development"))
    print("Bot is ready.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You are missing a required argument.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You don\'t have permissions to use this command.')
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    

    if message.mentions: # For AFK
        for mention in message.mentions:
            data = await bot.afk.find(mention.id)
            if data:
                await message.channel.send(f'{message.author.mention}, {mention.name} is currently AFK. Reason: {data["reason"]}')
            else:
                pass

    data = await bot.afk.find(message.author.id)
    if data and "reason" in data:
        await bot.afk.unset({"_id":message.author.id, "nick": 1, "reason": 1})
        await message.channel.send('Welcome back, {}! I have removed your AFK.'.format(message.author.name), delete_after=8)
        await message.author.edit(nick=data["nick"])
    else:
        pass

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["Cluster0"]
    bot.afk = Document(bot.db, "config")
    bot.tags = Document(bot.db, "tags")
    bot.cases = Document(bot.db, "cases")
    bot.botactivity = Document(bot.db, "botactivity")
    bot.botstatus = Document(bot.db, "botstatus")
    bot.counter = Document(bot.db, "counter")
    bot.uptime = Document(bot.db, "uptime")
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f'cogs.{file[:-3]}')
    bot.run(bot.config_token)
    
        

