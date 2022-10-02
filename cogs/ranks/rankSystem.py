import discord
from discord_slash.context import SlashContext
from ..matches import actions
from ..matches import constants as matchConstants
from . import constants
import datetime

from discord.member import Member


players = {}
# "59438543": {
#     "name": "9578439574",
#     "avatar": "543543",
#     "score": 650948,
#     "rank": 4
# }


# member = {
#     "_id": ctx.author.id,
#     "avatar": ctx.author.avatar_url._url,
#     "name": ctx.author.name,
# }

async def getRegion(member: Member):
    roles = member.roles
    if discord.utils.get(roles, id=913496131349119017):
        return "Asia"
    elif discord.utils.get(roles, id=913495608067764264):
        return "US"
    return "EU"
    
async def getPlatform(member: Member):
    roles = member.roles
    if discord.utils.get(roles, id=913495768214700073):
        return "psn"
    elif discord.utils.get(roles, id=913495739571769364):
        return "xbox"
    return "pc"

async def checkRankup(currentScore):
    return int((currentScore*2) + currentScore/(0.25*100))


async def rankCheck(score):
    nextRankScore = 5000
    currentRank = 1
    while score > nextRankScore:
        currentRank += 1
        nextRankScore = await checkRankup(nextRankScore)
    return currentRank, nextRankScore


async def updateDb(self):
    global players
    for id, player in players.items():
        try:
            await self.bot.ranking.upsert({
                "_id": id,
                **player
            })
        except:
            pass
    players = await self.bot.ranking.get_all_id()


async def rankUp(member: Member, newRank, oldRank):
    try:
        role = discord.utils.get(member.guild.roles, name=f"Rank {newRank}")
        await member.add_roles(role, "rankup!")
    except:
        pass
    try:
        role = discord.utils.get(member.guild.roles, name=f"Rank {oldRank}")
        await member.remove_roles(role, "removing old rank!")
    except:
        pass


async def firstRank(member: Member):
    try:
        role = discord.utils.get(member.guild.roles, name=f"Rank 1")
        await member.add_roles(role)
    except:
        pass


async def addRank(member: Member, amount: int):
    global players
    if str(member.id) in players.keys():
        score = players[str(member.id)]["score"] + amount
        oldRank = players[str(member.id)]["rank"]
        newRank, nextRankScore = await rankCheck(score)
        # TODO: add levelup thing
        if newRank > oldRank:
            await rankUp(member, newRank, oldRank)
            rankName = "Lord"
            if 0 <= newRank-1 < len(constants.rankNames):
                rankName = constants.rankNames[newRank-1]
            embed = discord.Embed(
                color=0x00FF00,
                description=f"{matchConstants.QUEUEEMOJI} Contratulations, You have reached Rank{rankName} (Rank {newRank}) on the Battlefield Prime Discord server!"
            )
            region = await getRegion(member)
            platform = await getPlatform(member)
            await member.send(embed=embed)
            players[str(member.id)] = {
                "name": member.name,
                "avatar": member.avatar_url._url,
                "score": score,
                "nextRankScore": nextRankScore,
                "rank": newRank,
                "region": region,
                "platform": platform
            }
        else:
            players[str(member.id)]["name"] = member.name
            players[str(member.id)]["avatar"] = member.avatar_url._url
            players[str(member.id)]["score"] = score
            players[str(member.id)]["nextRankScore"] = nextRankScore
            players[str(member.id)]["rank"] = newRank
    else:
        await firstRank(member)
        region = await getRegion(member)
        platform = await getPlatform(member)
        players[str(member.id)] = {
            "name": member.name,
            "avatar": member.avatar_url._url,
            "score": amount,
            "nextRankScore": 5000,
            "rank": 1,
            "region": region,
            "platform": platform
        }


async def getRank(member):
    global players
    if str(member.id) in players.keys():
        return players[str(member.id)]
    else:
        return {
            "name": member.name,
            "avatar": member.avatar_url._url,
            "score": 0,
            "nextRankScore": 5000,
            "rank": 1,
            "region": "EU",
            "platform": "pc"
        }


async def updateMatchMultiple(self, current):
    total = datetime.datetime.now() - current["starttime"]
    if total > datetime.timedelta(minutes=15):
        members = await actions.getAllMembers(self, current)
        for member in members:
            try:
                await addRank(member, 500)
            except:
                pass
