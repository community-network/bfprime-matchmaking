import asyncio
from discord.ext import commands
from discord.ext.commands.bot import AutoShardedBot
from .ranks import rankSystem, messageCreation
from discord_slash import cog_ext, SlashContext


class Ranking(commands.Cog):
    
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        """runs on ready"""
        while True:
            try:
                await rankSystem.updateDb(self)
                await asyncio.sleep(3600)
            except:
                pass
        
    @cog_ext.cog_slash(name="rank", description="See your current rank")
    async def getRank(self, ctx: SlashContext):
        await messageCreation.getRank(self, ctx)

def setup(bot):
    bot.add_cog(Ranking(bot))