from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord.message import Message
from discord_slash.utils.manage_commands import create_choice, create_option
from .matches import onClick, onCommand, constants, events
from .ranking import rankSystem
from discord_slash import cog_ext, SlashContext
from discord_slash.context import ComponentContext


class Matching(commands.Cog):
    """origin-api's Battlefield cog"""

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """runs on ready"""
        await events.onReady(self)

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        await onClick.clickListener(self, ctx)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.guild != None and message.guild.id == 910482518598365225:
            await rankSystem.addRank(message.author, 50)

    @cog_ext.cog_slash(name="match")
    async def baseMatch(self, ctx: SlashContext):
        pass

    @cog_ext.cog_subcommand(
        base="match",
        name="start",
        description="Opens a Battlefield Prime match. Visit https://bfprime.gg/matchmaker to learn more",
        options=[
            create_option(
                name="mode",
                description="Is the match a BF Prime match?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="BF Prime",
                        value="prime"
                    ),
                    create_choice(
                        name="Custom",
                        value="custom"
                    )
                ]),
            create_option(
                name="region",
                description="For which region?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Europe",
                        value="EU"
                    ),
                    create_choice(
                        name="North America",
                        value="NA"
                    ),
                    create_choice(
                        name="Asia & Oceania",
                        value="Asia"
                    )
                ]),
            create_option(
                name="groupsize",
                description="How many players?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="5 vs 5",
                        value="5v5"
                    ),
                    create_choice(
                        name="4 vs 4",
                        value="4v4"
                    ),
                    create_choice(
                        name="3 vs 3",
                        value="3v3"
                    ),
                    create_choice(
                        name="2 vs 2",
                        value="2v2"
                    )
                ]),
            create_option(
                name="map",
                description="Which map?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Arica Harbor",
                        value="Arica"
                    ),
                    create_choice(
                        name="Noshar Canals",
                        value="Nosh"
                    ),
                    create_choice(
                        name="Any",
                        value="Any"
                    )
                ]),
            create_option(
                name="teammatch",
                description="Is your team pre-made?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="No",
                        value="no"
                    ),
                    create_choice(
                        name="Yes",
                        value="yes"
                    )
                ]),
            create_option(
                name="starttime",
                description="In how many minutes do you want to start? (max 60 minutes, 0 to start now)",
                option_type=4,
                required=True,
                choices=[
                    create_choice(
                        name="Now",
                        value=0
                    ),
                    create_choice(
                        name="15 minutes",
                        value=15
                    ),
                    create_choice(
                        name="30 minutes",
                        value=30
                    ),
                    create_choice(
                        name="45 minutes",
                        value=45
                    ),
                    create_choice(
                        name="1 hour",
                        value=60
                    )
                ]),
        ])
    async def startMatch(self, ctx: SlashContext, mode: str, region: str, groupsize: str, map: str, teammatch: str = "no", starttime: int = 0):
        # dont use in DM's
        if ctx.guild == None:
            await ctx.send(f"Command can only be used inside a Discord server, not in DM's.")
        elif ctx.channel == None:
            await ctx.send(f"Command cant be used inside a thread #️⃣.")
        else:
            if starttime > 60:
                starttime = 60
            elif starttime < 0:
                starttime = 0
            if teammatch == "yes":
                isTeamMatch = True
            else:
                isTeamMatch = False
            # option has to exist
            if region in constants.REGIONFLAGS.keys() and groupsize in constants.LEFTGROUPSIZE.keys() and map in constants.MAPS.keys():
                await onCommand.createActivity(self, ctx, mode, region, groupsize, map, starttime, isTeamMatch)

    @cog_ext.cog_subcommand(
        base="match",
        name="close",
        description="Leaves or cancels your match & removes you from the que"
    )
    async def stopMatch(self, ctx: SlashContext):
        await onCommand.closeActivity(self, ctx)

    @cog_ext.cog_subcommand(
        base="match",
        name="help",
        description="Learn more about this bot and how it works"
    )
    async def help(self, ctx: SlashContext):
        await onCommand.helpCommand(self, ctx)

    @cog_ext.cog_subcommand(
        base="match",
        name="join",
        description="automatically join any open match in your region (que) instead of searching for a match",
        options=[
            create_option(
                name="region",
                description="For which region?",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Europe",
                        value="EU"
                    ),
                    create_choice(
                        name="North America",
                        value="NA"
                    ),
                    create_choice(
                        name="Asia & Oceania",
                        value="Asia"
                    )
                ]),
        ])
    async def queueMatch(self, ctx: SlashContext, region: str):
        if ctx.guild == None:
            await ctx.send(f"Command can only be used inside a Discord server, not in DM's.")
        else:
            if region in constants.REGIONFLAGS.keys():
                await onCommand.queueMatch(self, ctx, region)


def setup(bot):
    bot.add_cog(Matching(bot))
