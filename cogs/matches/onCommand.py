import datetime
import uuid
import discord
from discord_slash.context import SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
from . import onClick, messageCreation, constants, actions
from ..ranks import rankSystem


async def createActivity(self, ctx: SlashContext, mode: str, region: str, groupsize: str, map: str, starttime: int, teammatch: bool):
    # remove from queue when starting your own match
    await self.bot.queue.delete_by_id(ctx.author.id)
    otherMatches = await self.bot.matches.find_more({f'players.{ctx.author.id}': {"$exists": True}})
    if len(otherMatches) == 0:
        now = datetime.datetime.now()
        newstr = ''.join((ch if ch in '0123456789.-e' else ' ')
                         for ch in groupsize)
        listOfNumbers = [float(i) for i in newstr.split()]
        match = {
            "_id": ctx.author.id,
            "guildId": ctx.guild.id,
            "author": ctx.author.name,
            "authorId": ctx.author.id,
            "mode": mode, #prime or custom
            "playerMessages": [],
            "players": {str(ctx.author.id): {"name": ctx.author.name, "avatar": ctx.author.avatar_url._url}},
            "map": map,
            "region": region,
            "starttime": now + datetime.timedelta(minutes=starttime),
            "groupsize": groupsize,
            "playerAmount": 1,
            "maxPlayerAmount": int(sum(listOfNumbers)),
            "createdAt": now,
            "channelIds": [],
            "teamMatch": teammatch,
            "categoryId": None,
            "hasStarted": False,
            "isFullMsg": False,
            "hasEnded": False,
            "origChannel": ctx.channel.id,
            "origMessage": None,
            "ownerMessage": None,
            "failed": False
        }
        embed = await messageCreation.createMessage(match)
        originMessage = await ctx.send(embed=embed, components=[create_actionrow(
            create_button(
                style=ButtonStyle.green,
                label="Enter match",
                custom_id=f"enter.{ctx.author.id}",
                emoji=discord.utils.get(
                    self.bot.emojis, name="add", guild_id=910482518598365225)
            ),
            create_button(
                style=ButtonStyle.red,
                label="Leave match",
                custom_id=f"exit.{ctx.author.id}",
                emoji=discord.utils.get(
                    self.bot.emojis, name="exit", guild_id=910482518598365225)
            ),
            create_button(
                style=ButtonStyle.URL,
                label="Help",
                url="https://bfprime.gg/matchmaker",
                emoji=discord.utils.get(
                    self.bot.emojis, name="prime", guild_id=910482518598365225)
            ),
        )])
        match["origMessage"] = originMessage.id
        await self.bot.matches.insert(match)
        await ctx.channel.create_thread(name=f"🏆 {match['author']}'s Prime Match", minutes=60+starttime, message=originMessage)
    else:
        await ctx.send(f"Please leave all other matches you're in before opening your own!")


async def closeActivity(self, ctx: SlashContext):
    if ctx.guild != None:
        otherMatches = await self.bot.matches.find_one({f"players.{ctx.author.id}": { "$exists": True }})
        if otherMatches != None:
            if otherMatches["authorId"] == ctx.author.id:
                await onClick.onCancel(self, ctx, otherMatches, otherMatches["_id"])
                await ctx.send(f"Match cancelled, I have notified all players that entered the match.")
            else:
                await onClick.onLeave(self, ctx, otherMatches, otherMatches["_id"])
                await ctx.send(f"You left the match of \"{otherMatches['author']}\".")
        else:
            queue = await self.bot.queue.find(ctx.author.id)
            if queue != None:
                await self.bot.queue.delete_by_id(ctx.author.id)
                await ctx.send(f"You have been removed from queue.")
            else:
                await ctx.send(f"You dont have any matches to close.")
    else:
        await ctx.send(f"Command can only be used inside a Discord server, not in DM's.")


async def helpCommand(self, ctx: SlashContext):
    embed = discord.Embed(
        color=0x00ffff,
        description='For more info about the matchmaker, visit the attached link below.'
    )
    await ctx.send(embed=embed, components=[create_actionrow(
        create_button(
            style=ButtonStyle.URL,
            label="bfprime.gg/matchmaker",
            url="https://bfprime.gg/matchmaker",
            emoji=discord.utils.get(
                self.bot.emojis, name="prime", guild_id=910482518598365225)
        ))])


async def queueMatch(self, ctx: SlashContext, region: str):
    queue = await self.bot.queue.find(ctx.author.id)
    match = await self.bot.matches.find_one({f"players.{ctx.author.id}": { "$exists": True }})
    if match != None:
        await ctx.send("You are already in another match!")
    elif queue != None:
        await ctx.send("You are already in the queue, please wait for a new match.")
    else:
        rank = await rankSystem.getRank(ctx.author)
        teamName = await actions.getTeam(ctx.author)
        queue = {
            "_id": ctx.author.id,
            "avatar": ctx.author.avatar_url._url,
            "name": ctx.author.name,
            "region": region,
            "guildId": ctx.guild.id,
            "rank": rank["rank"],
            "rankScore": rank["score"],
            "teamName": teamName
        }
        await self.bot.queue.insert(queue)
        embed = discord.Embed(
            color=0x00ffff,
            description=f'{constants.QUEUEEMOJI} Joined the {region} Queue'
        )
        await ctx.send(embed=embed, components=[create_actionrow(
            create_button(
                style=ButtonStyle.URL,
                label="Help",
                url="https://bfprime.gg/matchmaker",
                emoji=discord.utils.get(
                    self.bot.emojis, name="prime", guild_id=910482518598365225)
            ))])
        
