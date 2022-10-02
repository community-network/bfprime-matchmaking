import io
import discord
from discord_slash.context import SlashContext
from . import image, rankSystem

async def getRank(self, ctx: SlashContext):
    currentRank = await rankSystem.getRank(ctx.author)
    region = await rankSystem.getRegion(ctx.author)
    platform = await rankSystem.getPlatform(ctx.author)
    img = await image.render(currentRank, region, platform)
    with io.BytesIO() as data_stream:
        img.save(data_stream, format="png")
        data_stream.seek(0)
        discordImage = discord.File(data_stream, filename="test.png")
        await ctx.send(file=discordImage)
    