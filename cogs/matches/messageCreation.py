import datetime
import discord
from . import constants


async def getMessage(self, current):
    guild = self.bot.get_guild(current["guildId"])
    channel = guild.get_channel(current["origChannel"])
    return await channel.fetch_message(current["origMessage"])


async def createOwnerMessage(match):
    description = f"""
        Your {match["groupsize"]} match on {constants.MAPNAMES[match["map"]]} is ready! - Please start it now
        {match["playerAmount"]}/{match["maxPlayerAmount"]} Players are in the match
    """
    embed = discord.Embed(
        color=0x00FF00,
        title=f'{constants.LEFTGROUPSIZE[match["groupsize"]]}{constants.VERSUS}{constants.RIGHTGROUPSIZE[match["groupsize"]]} | Match ready to start',
        description=description
    )
    playerList = []
    for playerId, player in match["players"].items():
        playerList.append(player["name"])
    embed.add_field(name=f"Players", value="• " +
                    "\n• ".join(playerList))
    embed.set_thumbnail(
        url=constants.MAPIMAGES[match["map"]])
    return embed


async def createMessage(match):
    now = datetime.datetime.now()
    total = now - match["starttime"]
    if total > datetime.timedelta(hours=2):
        description = "Match expired"
        color = 0xed4245
    elif match["failed"]:
        description = "Failed to create"
        color = 0xed4245
    elif match["hasEnded"]:
        color = 0xed4245
        if match["maxPlayerAmount"] == 0:
            description = "Match was cancelled by the host"
        else:
            color = 0x252626
            description = "Match ended"
    else:
        if match["hasStarted"]:
            color = 0x00ffff
            description = f"""
                Match Now Live
                {match["playerAmount"]}/{match["maxPlayerAmount"]} Players in match
            """
        else:
            color = 0x40a45f
            description = f"""
                Match not Live - Enter match to play
                {match["playerAmount"]}/{match["maxPlayerAmount"]} Players joined match
            """
    now = datetime.datetime.now()
    try:
        minutesToStart = round((match["starttime"] - now).total_seconds() / 60)
    except:
        minutesToStart = 0
    starttime = f"{constants.TIMEEMOJI} in {minutesToStart} minutes"
    if minutesToStart <= 0:
        starttime = "now"

    embed = discord.Embed(
        color=color,
        title=f'{constants.LEFTGROUPSIZE[match["groupsize"]]}{constants.VERSUS}{constants.RIGHTGROUPSIZE[match["groupsize"]]} | {constants.MAPS[match["map"]]} | {constants.REGIONFLAGS[match["region"]]} | {starttime} | {constants.HOSTEMOJI} {match["author"]}',
        description=description
    )
    # if cancelled, show cancelled instead
    fieldTitle = ""
    if match["teamMatch"]:
        fieldTitle = f"{constants.PREMADEEMOJI} Premade vs an official team\n\n"
    if match["maxPlayerAmount"] != 0:
        playerList = []
        for playerId, player in match["players"].items():
            playerList.append(player["name"])
        embed.add_field(name=f"{fieldTitle}Players", value="• " +
                        "\n• ".join(playerList))
    else:
        embed.add_field(name=f"{fieldTitle}Match Cancelled", value="\u200b")
    embed.set_thumbnail(
        url=constants.MAPIMAGES[match["map"]])
    return embed
