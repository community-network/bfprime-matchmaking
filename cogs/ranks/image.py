import io
import os, random
from typing import Tuple
from PIL import Image, ImageFont, ImageDraw
import aiohttp
from . import constants
TRANSPARENCY = .75  # Degree of transparency, 0-100%
OPACITY = int(255 * TRANSPARENCY)
    
async def drawBorders(img: Image):
    boxes = Image.new('RGBA', img.size, (255,255,255,0))
    draw = ImageDraw.Draw(boxes, "RGBA")  
    draw.rectangle(((0, 0), (img.width, 119)), fill=(0, 0, 0, OPACITY))
    draw.rectangle(((0, 720), (img.width, img.height)), fill=(0, 0, 0, OPACITY))
    img = Image.alpha_composite(img, boxes)
    
    bfPrimeImg = Image.open(f"{os.path.dirname(os.path.realpath(__file__))}/images/iconPrime.png").convert('RGBA')
    bfPrimeImg.thumbnail((28, 28), Image.ANTIALIAS)
    img.paste(bfPrimeImg, (428, 22), bfPrimeImg)
    return img    
    
async def drawAvatar(img: Image, currentRank):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'https://cdn.discordapp.com{currentRank["avatar"]}') as r:
            avatarByte = await r.read()
    avatarImg = Image.open(io.BytesIO(avatarByte)).convert('RGBA')
    avatarImg = avatarImg.resize((120, 120), Image.ANTIALIAS)
    img.paste(avatarImg, (0, 0), avatarImg)
    
    draw = ImageDraw.Draw(img)
    NameFont = ImageFont.truetype(
        f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Roboto-Bold.ttf", size=34, index=0)
    draw.text((142, 20), str(currentRank["name"]), font=NameFont)
    
    return img

async def calcRank(current: int):
    if current % 4 == 0:
        return 4, "lvlup"
    elif current % 3 == 0:
        return 3, "gold"
    elif current % 2 == 0:
        return 2, "silver"
    else:
        return 1, "bronze"

async def drawRank(img: Image, rank: int):
    rankNum, iconName = await calcRank(rank)
    avatarImg = Image.open(f"{os.path.dirname(os.path.realpath(__file__))}/images/rankBackground/{iconName}.png").convert('RGBA')
    avatarImg.thumbnail((120, 120), Image.ANTIALIAS)
    img.paste(avatarImg, (484, 0), avatarImg)
    draw = ImageDraw.Draw(img)
    rankFont = ImageFont.truetype(
        f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Roboto-Black.ttf", size=40, index=0)
    draw.text((530, 37), str(rankNum), font=rankFont, fill=(0,0,0,255))
    
    rankName = "Lord"
    if 0 <= rank-1 < len(constants.rankNames):
        rankName = constants.rankNames[rank-1]

    descriptionFont = ImageFont.truetype(
        f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Roboto-Bold.ttf", size=24, index=0)
    draw.text((142, 67), str(rankName), font=descriptionFont)
    
    img = await drawIcon(img, f"{os.path.dirname(os.path.realpath(__file__))}/images/ranks/black-{str(rankNum).zfill(2)}.png", (429, 64))
    return img

async def drawXp(img: Image, amount: int, nextRank: int):
    draw = ImageDraw.Draw(img)
    XPFont = ImageFont.truetype(
        f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Roboto-Bold.ttf", size=26, index=0)
    amountFont = ImageFont.truetype(
        f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Roboto-Black.ttf", size=26, index=0)
    draw.text((26, 744), str("XP"), font=XPFont)
    draw.text((66, 743), str("|"), font=XPFont, fill=(100, 100, 100))
    draw.text((78, 744), str(str(amount).zfill(4)), font=amountFont, fill=(0, 255, 222))
    draw.text((140, 744), str("/"), font=amountFont, fill=(100, 100, 100))
    draw.text((150, 744), str(str(nextRank).zfill(4)), font=amountFont, fill=(100, 100, 100))
    return img
    
async def drawIcon(img: Image, image: str, location: Tuple[int, int]):
    customImage = Image.open(image).convert('RGBA')
    customImage.thumbnail((34, 34), Image.ANTIALIAS)
    img.paste(customImage, location, customImage)
    return img
    
async def render(currentRank, region: str, platform: str):
    randomImage = random.choice(os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}/images/backgrounds/"))
    img = Image.open(
        f"{os.path.dirname(os.path.realpath(__file__))}/images/backgrounds/{randomImage}").convert("RGBA")
    img = await drawBorders(img)
    img = await drawAvatar(img, currentRank)
    img = await drawRank(img, currentRank["rank"])
    img = await drawXp(img, currentRank["score"], currentRank["nextRankScore"])
    # platform
    img = await drawIcon(img, f"{os.path.dirname(os.path.realpath(__file__))}/images/platforms/{platform}.png", (500, 743))
    # region
    img = await drawIcon(img, f"{os.path.dirname(os.path.realpath(__file__))}/images/regions/{region}.png", (546, 743))
    return img