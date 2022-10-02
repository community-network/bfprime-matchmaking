import discord
from discord import embeds
from . import messageCreation, actions, constants
from ..ranking import rankSystem
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button


async def clickListener(self, ctx: ComponentContext):
    componentInfo = ctx.custom_id.split(".")
    matchId = int(componentInfo[1])
    current = await self.bot.matches.find(matchId)
    message = componentInfo[0]
    # if match exist
    if current != None:
        # click type
        if message == "enter" and current["hasStarted"] == False:
            member = {
                "_id": ctx.author.id,
                "avatar": ctx.author.avatar_url._url,
                "name": ctx.author.name,
            }
            await onEnter(self, ctx, member, current, matchId)
        elif message == "start" and current["hasStarted"] == False:
            await onStart(self, ctx, current, matchId)
        elif message == "cancel" and current["hasStarted"] == False:
            await onCancel(self, ctx, current, matchId)
        elif message == "exit":
            await onLeave(self, ctx, current, matchId)
        elif message == "exitFromQue":
            embed = discord.Embed(
                color=0x00ffff,
                description=f"{constants.QUEUEEMOJI} you've left the match"
            )
            await ctx.edit_origin(embed=embed, components=[])
            await onLeave(self, ctx, current, matchId)
        elif message == "end" and current["hasStarted"] == True:
            if ctx.author.id == current["authorId"]:
                await rankSystem.updateMatchMultiple(self, current)
                await onDelete(self, ctx, current, matchId)


async def onEnter(self, ctx: ComponentContext, member, current, matchId: str):
    otherMatches = await self.bot.matches.find_one({f"players.{member['_id']}": {"$exists": True}})
    if otherMatches != None and ctx != None:
        if otherMatches["authorId"] == ctx.author.id:
            await ctx.send(f"You cant join multiple matches, You already have your own!")
        else:
            await ctx.send(f"You cant join multiple matches, Your already in the match of \"{otherMatches['author']}\".")
    else:
        if ctx == None:
            await addUser(self, None, current, member, matchId)
        elif str(ctx.author.id) not in current["players"].keys() and current["playerAmount"] < current["maxPlayerAmount"]:
            await addUser(self, ctx, current, member, matchId)


async def addUser(self, ctx, current, member, matchId):
    await self.bot.queue.delete_by_id(member["_id"])
    current = await actions.addPlayer(self, member, current)
    embed = await messageCreation.createMessage(current)
    if current["origMessage"] != None:
        origMessage = await messageCreation.getMessage(self, current)
        await origMessage.edit(embed=embed)
    else:
        await ctx.edit_origin(embed=embed)
    await actions.editPingOwner(self, None, current, matchId)


async def onStart(self, ctx: ComponentContext, current, matchId: str):
    current = await self.bot.matches.find(matchId)
    current["hasStarted"] = True
    embed = await messageCreation.createMessage(current)
    guild = self.bot.get_guild(current["guildId"])
    current, members, invite = await actions.createChannels(self, guild, current)
    components = [create_actionrow(
        create_button(
            style=ButtonStyle.URL,
            label="Enter match voicelobby",
            url=invite.url,
            emoji=discord.utils.get(
                self.bot.emojis, name="voice", guild_id=910482518598365225)
        ),
        create_button(
            style=ButtonStyle.red,
            label="End match",
            custom_id=f"end.{matchId}",
            emoji=discord.utils.get(
                self.bot.emojis, name="exit", guild_id=910482518598365225)
        ),
    )]
    if current["origMessage"] != None:
        origMessage = await messageCreation.getMessage(self, current)
        await origMessage.edit(embed=embed, components=components)
    for member in members:
        try:
            if member.id == current["authorId"]:
                playerMessage = await member.send(embed=embed, components=[create_actionrow(
                    create_button(
                        style=ButtonStyle.URL,
                        label="Enter match voicelobby",
                        url=invite.url,
                        emoji=discord.utils.get(
                            self.bot.emojis, name="voice", guild_id=910482518598365225)
                    ),
                    create_button(
                        style=ButtonStyle.red,
                        label="End match",
                        custom_id=f"end.{matchId}",
                        emoji=discord.utils.get(
                            self.bot.emojis, name="exit", guild_id=910482518598365225)
                    ))
                ])
            else:
                playerMessage = await member.send(embed=embed, components=[create_actionrow(
                    create_button(
                        style=ButtonStyle.URL,
                        label="Enter match voicelobby",
                        url=invite.url
                    ))
                ])
            current["playerMessages"].append(
                {"ownerId": member.id, "messageId": playerMessage.id})
        except:
            pass
    await self.bot.matches.upsert(current)
    await ctx.edit_origin(components=[])


async def onLeave(self, ctx: ComponentContext, current, matchId: str):
    if str(ctx.author.id) in current["players"].keys():
        current = await actions.delPlayer(self, ctx, current)
        embed = await messageCreation.createMessage(current)
        if ctx.author.id == current["authorId"]:
            current["maxPlayerAmount"] = 0
            await onDelete(self, ctx, current, matchId)
        else:
            if current["origMessage"] != None:
                origMessage = await messageCreation.getMessage(self, current)
                await origMessage.edit(embed=embed)
            else:
                await ctx.edit_origin(embed=embed)
        if current["ownerMessage"] != None:
            await actions.editPingOwner(self, None, current, matchId)


async def onDelete(self, ctx: ComponentContext, current, matchId: str):
    guild = self.bot.get_guild(current["guildId"])
    category = discord.utils.get(
        guild.categories, id=current["categoryId"])
    if category != None:
        for channel in category.channels:
            await channel.delete()
        await category.delete()
    current["hasEnded"] = True
    embed = await messageCreation.createMessage(current)
    if current["origMessage"] != None:
        origMessage = await messageCreation.getMessage(self, current)
        await origMessage.edit(embed=embed, components=[])
    if current["ownerMessage"] != None:
        try:
            owner = await guild.fetch_member(current["authorId"])
            originMessage = await owner.fetch_message(current["ownerMessage"])
            await originMessage.delete()
        except:
            pass
    if current["playerMessages"] != []:
        for message in current["playerMessages"]:
            try:
                messageOwner = await guild.fetch_member(message["ownerId"])
                originMessage = await messageOwner.fetch_message(message["messageId"])
                await originMessage.edit(embed=embed, components=[])
            except:
                pass
    await self.bot.matches.delete(matchId)


async def onCancel(self, ctx: ComponentContext, current, matchId: str):
    current["maxPlayerAmount"] = 0
    current["hasEnded"] = True
    await onDelete(self, ctx, current, matchId)
    embed = await messageCreation.createMessage(current)
    members = await actions.getAllMembers(self, current)
    for member in members:
        await member.send(embed=embed)


async def onExpire(self, ctx: ComponentContext, current, matchId: str):
    embed = await messageCreation.createMessage(current)
    members = await actions.getAllMembers(self, current)
    for member in members:
        await member.send(embed=embed)
    await onDelete(self, ctx, current, matchId)
