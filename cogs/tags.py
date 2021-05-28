import discord
from datetime import datetime
from discord.ext import commands
from utils.secrets import TAG_BLACKLIST_ROLE, MOD_ROLE_NAME, MOD_ROLE_ID


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.group(invoke_without_command=True, aliases=['t'])
    async def tag(self, ctx, *, tag: commands.clean_content=None):
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

    @tag.command(aliases=['+'])
    async def create(self, ctx, tagname: commands.clean_content, *, content: commands.clean_content):
        """Creates a new tag."""
        notag = discord.utils.get(ctx.guild.roles, id=TAG_BLACKLIST_ROLE)
        if notag in ctx.author.roles:
            return await ctx.send('You can\'t do this.')

        data = await self.bot.tags.find(tagname)
        if data:
            return await ctx.send('A tag with that name already exists.')

        if tagname != tagname.lower():
            tagname = tagname.lower()
            note = "(the tag has been created all in lowercase.)"
        else:
            note = ""
        try:
            await self.bot.tags.upsert(
                {
                    "_id": str(tagname),
                    "content": str(content),
                    "createdAt": str(datetime.utcnow()),
                    "createdBy": ctx.author.id,
                    "guild": ctx.guild.id,
                }
            )
            await ctx.send(f':ok_hand: **{tagname}** successfully created. {note}', allowed_mentions=None)

        except Exception as e:
            return await ctx.send('Failed to create that tag. ```{}```'.format(e))

    @tag.command(aliases=['-'])
    async def delete(self, ctx, *, tagname: commands.clean_content):
        """Deletes a tag. You must be the tag creator or a moderator to delete tags."""
        data = await self.bot.tags.find(tagname)
        mrole = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        if str(ctx.author) == data["createdBy"]:
            pass
        elif mrole in ctx.author.roles:
            pass
        else:
            return await ctx.send('You can\'t do this. You must either be the tag creator or be a moderator.')

        await self.bot.tags.delete_by_id(tagname)

        await ctx.send(f':ok_hand: **{tagname}** successfully deleted.', allowed_mentions=None)

    @tag.command(aliases=['delinvoke', 'di'])
    async def delete_invoke(self, ctx, *, tagname: commands.clean_content):
        """Toggles deleting the invocation of a certain tag. You must either be the tag creator or a moderator to do this."""
        data = await self.bot.tags.find(tagname)
        modrole = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        if data["createdBy"] != ctx.author or data["createdBy"] != ctx.author.id:
            if modrole not in ctx.author.roles:
                return await ctx.send('You can\'t do this to tags that you don\'t own.')

        if "delInvoke" in data:
            if data["delInvoke"] == True:
                await self.bot.tags.upsert({"_id": str(tagname), "delInvoke": False})
        else:
            await self.bot.tags.upsert({"_id": str(tagname), "delInvoke": True})

        await ctx.send(f':ok_hand: The message invocation to **{tagname}** will now be deleted.')

    @tag.command(aliases=['i'])
    async def info(self, ctx, *, tagname: commands.clean_content):
        """Shows info on a certain tag."""
        data = await self.bot.tags.find(tagname)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        length = len(data["content"])

        e = discord.Embed(
            title=data["_id"],
            description=f'Created: {data["createdAt"]} UTC\nCreator: {data["createdBy"]}\nTag content length: {length}',
            color=discord.Color.blue()
        )
        await ctx.send(embed=e)

    @tag.command(name='list', aliases=['all'])
    async def _list(self, ctx):
        """Lists all of the current tags."""
        data = await self.bot.tags.get_all()
        e = discord.Embed(
            title='All tags',
            description=", ".join([str(d.get("_id")) for d in data]),
            color=discord.Color.blue()
        )
        await ctx.send(embed=e)

    @tag.command(name='edit', aliases=['e'])
    async def _edit(self, ctx, tagname: commands.clean_content, *, content: commands.clean_content):
        """Edits the content of a tag.

        You can use ?tag raw to get the raw content of an existing tag.
        """
        data = await self.bot.tags.find(tagname)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        modrole = ctx.guild.get_role(MOD_ROLE_ID)

        if modrole not in ctx.author.roles:
            if data["createdBy"] != ctx.author:
                if data["createdBy"] != ctx.author.id:
                    return await ctx.send('You don\'t own this tag.')

        await self.bot.tags.upsert({"_id": tagname, "content": str(content)})
        await ctx.send(f':ok_hand: **{tagname}** successfully edited.')

    @tag.command(name='block')
    @commands.has_role(MOD_ROLE_NAME)
    async def _block(self, ctx, *, member: discord.Member):
        role = ctx.guild.get_role(TAG_BLACKLIST_ROLE)
        if role in member.roles:
            await member.remove_roles(role)
            return await ctx.send('Unblocked.')
        try:
            await member.add_roles(TAG_BLACKLIST_ROLE)
        except Exception as e:
            await ctx.send('Can\'t do that. ```{e}```'.format(e))

    @tag.command(name='raw')
    async def _raw(self, ctx, *, tagname: commands.clean_content):
        """Gets the raw content of a message. This is useful for editing tags."""
        data = await self.bot.tags.find(tagname)
        if not data:
            return await ctx.send('Unable to find a tag with that name.')

        await ctx.send(f"```{data['content']}```")

    @tag.error
    async def tag_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('Missing a required argument.')


def setup(bot):
    bot.add_cog(Tags(bot))