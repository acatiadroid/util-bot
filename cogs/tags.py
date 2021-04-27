import discord
from datetime import datetime
from discord.ext import commands

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.group(invoke_without_command=True, aliases = ['t'])
    async def tag(self, ctx, *, tag=None):
        """Performs a tag."""
        data = await self.bot.tags.find(tag)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')
        
        try:
            await ctx.send(data["content"], allowed_mentions=None)
            if "delInvoke" in data:
                if data["delInvoke"] == True:
                    await ctx.message.delete()
        except Exception as e:
            await ctx.send(f'Failed to send tag: ```{e}```', allowed_mentions=None)
    
    @tag.command(aliases = ['+'])
    async def create(self, ctx, tagname, *, content):
        """Creates a new tag."""
        notag = discord.utils.get(ctx.guild.roles, name = 'No Tags')
        if notag in ctx.author.roles:
            return await ctx.send('You can\'t do this.')
        
        data = await self.bot.tags.find(tagname)
        if data:
            return await ctx.send('A tag with that name already exists.')

        try:
            await self.bot.tags.upsert(
                {
                    "_id": str(tagname),
                    "content": str(content),
                    "createdAt": str(datetime.utcnow()),
                    "createdBy": str(ctx.author),
                    "guild": ctx.guild.id,
                }
            )
            await ctx.send(f'**{tagname}** successfully created. :ok_hand:', allowed_mentions=None)
            
        except Exception as e:
            return await ctx.send('Failed to create that tag. ```{}```'.format(e))

    @tag.command(aliases = ['-'])
    async def delete(self, ctx, *, tagname):
        """Deletes a tag. You must be the tag creator or a moderator to delete tags."""
        data = await self.bot.tags.find(tagname)
        mrole = discord.utils.get(ctx.guild.roles, name = 'Moderator')
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        if str(ctx.author) == data["createdBy"]:
            pass
        elif mrole in ctx.author.roles:
            pass
        else:
            return await ctx.send('You can\'t do this. You must either be the tag creator or be a moderator.')
        
        await self.bot.tags.delete_by_id(tagname)

        await ctx.send(f'**{tagname}** successfully deleted. :ok_hand:', allowed_mentions=None)

    @tag.command(aliases = ['delinvoke', 'di'])
    async def delete_invoke(self, ctx, *, tagname):
        """Toggles deleting the invocation of a certain tag. You must either be the tag creator or a moderator to do this."""
        data = await self.bot.tags.find(tagname)
        modrole = discord.utils.get(ctx.guild.roles, name = 'Moderator')
        if not data:
            return await ctx.send('Unable to find a tag with that name.')
        
        if data["createdBy"] != ctx.author:
            if modrole not in ctx.author.roles:
                return await ctx.send('You can\'t do this to tags that you don\'t own.')
        
        if "delInvoke" in data:
            if data["delInvoke"] == True:
                await self.bot.tags.upsert({"_id": str(tagname), "delInvoke": False})
        else:
            await self.bot.tags.upsert({"_id":str(tagname), "delInvoke": True})

        await ctx.send(f'The message invocation to **{tagname}** will now be deleted. :ok_hand:')

    @tag.command(aliases = ['i'])
    async def info(self, ctx, *, tagname):
        """Shows info on a certain tag."""
        data = await self.bot.tags.find(tagname)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        length = len(data["content"])

        e = discord.Embed(
            title = data["_id"],
            description = f'Created: {data["createdAt"]} UTC\nCreator: {data["createdBy"]}\nTag content length: {length}',
            color = discord.Color.blue()
        )
        await ctx.send(embed=e) 
    
    @tag.command(name='list', aliases = ['all'])
    async def _list(self, ctx):
        """Lists all of the current tags."""
        data = await self.bot.tags.get_all()
        e = discord.Embed(
            title = 'All tags',
            description = ", ".join([str(d.get("_id")) for d in data]),
            color = discord.Color.blue()
        )
        await ctx.send(embed=e)
    
    @tag.command(name = 'block')
    async def _block(self, ctx, *, member:discord.Member):
        modrole = ctx.guild.get_role('Moderator')
        if modrole not in ctx.author.roles:
            return await ctx.send('You can\'t do this.')

        role = ctx.guild.get_role(815313621835841587)
        if role in member.roles:
            return await ctx.send('They\'re already blocked from making tags.')
        try:
            await member.add_roles(815313621835841587)
        except Exception as e:
            await ctx.send('Can\'t do that. ```{e}```'.format(e))

    @tag.command(name='raw')
    async def _raw(self, ctx, *, tagname):
        data = await self.bot.tags.find(tagname)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')
        
        await ctx.send(embed=discord.Embed(description = f'```{data["content"]}```'))

    @tag.error
    async def tag_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('Missing a required argument.')    
    
def setup(bot):
    bot.add_cog(Tags(bot))