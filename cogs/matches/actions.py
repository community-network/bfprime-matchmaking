from typing import List
import discord
from discord.member import Member
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
from . import messageCreation


async def pingOwner(self, ctx: ComponentContext, current, matchId: str):
    if ctx != None:
        guild = ctx.guild
    else:
        guild = self.bot.get_guild(current["guildId"])
    owner = await guild.fetch_member(current["authorId"])
    embed = await messageCreation.createOwnerMessage(current)
    ownerMessage = await owner.send(embed=embed, components=[create_actionrow(
        create_button(
            style=ButtonStyle.green,
            label="Start match",
            custom_id=f"start.{matchId}",
            emoji=discord.utils.get(
                self.bot.emojis, name="add", guild_id=910482518598365225)
        ),
        create_button(
            style=ButtonStyle.red,
            label="Cancel match",
            custom_id=f"cancel.{matchId}",
            emoji=discord.utils.get(
                self.bot.emojis, name="exit", guild_id=910482518598365225)
        ),
        create_button(
            style=ButtonStyle.URL,
            label="Map codes",
            url="https://bfprime.gg/codes",
            emoji=discord.utils.get(
                self.bot.emojis, name="prime", guild_id=910482518598365225)
        ),
    )])
    current["ownerMessage"] = ownerMessage.id
    if await self.bot.matches.find(matchId) != None:
        await self.bot.matches.upsert(current)


async def onServerFull(self, ctx: ComponentContext, current, matchId: str):
    if ctx != None:
        guild = ctx.guild
    else:
        guild = self.bot.get_guild(current["guildId"])
    owner = await guild.fetch_member(current["authorId"])
    owner.send("Your match is now full 10/10 Players.")
    await self.bot.matches.upsert(current)


async def editPingOwner(self, ctx: ComponentContext, current, matchId: str):
    # run when ownerMessage to start match is there
    if current["ownerMessage"] != None:
        if ctx != None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(current["guildId"])
        owner = await guild.fetch_member(current["authorId"])
        try:
            originMessage = await owner.fetch_message(current["ownerMessage"])
            embed = await messageCreation.createOwnerMessage(current)
            await originMessage.edit(embed=embed)
        except:
            pass


async def createChannels(self, guild, current):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False),
    }
    members = await getAllMembers(self, current)
    for member in members:
        overwrites[member] = discord.PermissionOverwrite(connect=True)
    category = await guild.create_category(f"🔰 {current['author']}'s Prime Match", reason="match happening", position=99, overwrites=overwrites)
    lobby = await category.create_voice_channel("⚫ Matchmaking lobby", user_limit=current["maxPlayerAmount"])
    voice1 = await category.create_voice_channel("🔴 Team 1", user_limit=current["maxPlayerAmount"]/2)
    voice2 = await category.create_voice_channel("🔵 Team 2", user_limit=current["maxPlayerAmount"]/2)
    current["channelIds"] = [lobby.id, voice1.id, voice2.id]
    current["categoryId"] = category.id
    invite = await lobby.create_invite(reason="bot starting a match", max_age=7200)
    return current, members, invite


async def addPlayer(self, member, current):
    current["players"][str(member["_id"])] = {
        "name": member["name"], "avatar": member["avatar"]}
    current["playerAmount"] = len(current["players"])
    if current.get("_id", None) != None:
        current["_id"] = current["authorId"]
    await self.bot.matches.upsert(current)
    return current


async def delPlayer(self, ctx: ComponentContext, current):
    del current["players"][str(ctx.author.id)]
    current["playerAmount"] = len(current["players"].keys())
    if current.get("_id", None) != None:
        current["_id"] = current["authorId"]
    await self.bot.matches.upsert(current)
    return current


async def editMessage(self, current):
    embed = await messageCreation.createMessage(current)
    origMessage = await messageCreation.getMessage(self, current)
    await origMessage.edit(embed=embed)


async def getAllMembers(self, current):
    members: List[Member] = []
    for memberId in current["players"].keys():
        guild = self.bot.get_guild(current["guildId"])
        member = await guild.fetch_member(int(memberId))
        members.append(member)
    return members

async def getTeam(author: Member):
    for role in author.roles:
        if "TEAM | " in role.name:
            return role.name.split("|").strip()
    return None