import datetime
import asyncio
import discord
from discord_slash.model import ButtonStyle

from discord_slash.utils.manage_components import create_actionrow, create_button
from . import onClick, actions, constants

# checks all matches statuses


async def onReady(self):
    while True:
        await matches(self)
        await queue(self)
        await asyncio.sleep(10)


async def matches(self):
    try:
        matches = await self.bot.matches.get_all()
        now = datetime.datetime.now()
        for match in matches:
            await matchCheck(self, now, match)
    except Exception as e:
        print(f"match automation failed: {e}")


async def matchCheck(self, now, match):
    try:
        total = now - match["starttime"]
        # older than 1 day
        if total > datetime.timedelta(hours=2):
            await onClick.onExpire(self, None, match, match["authorId"])
        elif len(match["players"].keys()) >= match["maxPlayerAmount"] and match["isFullMsg"] == False and match["hasStarted"] == False:
            match["isFullMsg"] = True
            await actions.onServerFull(self, None, match, match["authorId"])
        elif now > match["starttime"] and match["ownerMessage"] == None:
            # on ready to start
            await actions.pingOwner(self, None, match, match["authorId"])
        elif now < match["starttime"]:
            await beforeStart(self, match)
    except Exception as e:
        print(f"match {match['authorId']} failed {e}")


async def beforeStart(self, match):
    if match["origMessage"] != None:
        await actions.editMessage(self, match)
    else:
        match["failed"] = True
        await onClick.onExpire(self, None, match, match["authorId"])


async def queue(self):
    queueUsers = await self.bot.queue.get_all()
    matches = await self.bot.matches.get_all()
    for user in queueUsers:
        await checkUser(self, user, matches)


async def checkUser(self, user, matches):
    for match in matches:
        if match["playerAmount"] < match["maxPlayerAmount"] and match["teamMatch"] == False and match["region"] == user["region"] and user["guildId"] == match["guildId"]:
            await onClick.onEnter(self, None, user, match, match["authorId"])
            guild = self.bot.get_guild(match["guildId"])
            member = await guild.fetch_member(int(user["_id"]))
            embed = discord.Embed(
                color=0x00FF00,
                description=f"{constants.QUEUEEMOJI} you've been added to {match['author']}'s match, we will notify you when it starts!"
            )
            try:
                playerMessage = await member.send(embed=embed, components=[create_actionrow(
                    create_button(
                        style=ButtonStyle.URL,
                        label="Help",
                        url="https://bfprime.gg/matchmaker",
                        emoji=discord.utils.get(
                            self.bot.emojis, name="prime", guild_id=910482518598365225)
                    ),
                    create_button(
                        style=ButtonStyle.red,
                        label="Leave match",
                        custom_id=f"exitFromQue.{match['authorId']}",
                        emoji=discord.utils.get(
                            self.bot.emojis, name="exit", guild_id=910482518598365225)
                    ))])
                match["playerMessages"].append(
                    {"ownerId": member.id, "messageId": playerMessage.id})
            except:
                pass
            match["_id"] = match["authorId"]
            await self.bot.matches.upsert(match)
