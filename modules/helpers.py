from PIL import Image
import discord
from main import bot

async def guild_emoji(guild):
    await guild.icon.save(f"tmp/{guild.id}.png")
    guild_icon = Image.open(f"tmp/{guild.id}.png").convert("RGB")
    mask = Image.open("assets/circle-mask.png").convert("L")
    mask = mask.resize((guild_icon.width, guild_icon.height))
    guild_icon.putalpha(mask)
    guild_icon = guild_icon.resize((64, 64))
    guild_icon.save(f"tmp/{guild.id}.png")
    
    testy = bot.get_guild(717048644708073534)
    return await testy.create_custom_emoji(name = guild.id, image = open(f"tmp/{guild.id}.png", "rb").read())

async def round_icon(icon):
    hashed = hash(icon)
    await icon.save(f"tmp/{hashed}.png")
    guild_icon = Image.open(f"tmp/{hashed}.png").convert("RGB")
    mask = Image.open("assets/circle-mask.png").convert("L")
    mask = mask.resize((guild_icon.width, guild_icon.height))
    guild_icon.putalpha(mask)
    guild_icon = guild_icon.resize((64, 64))
    guild_icon.save(f"tmp/{hashed}.png")
    return discord.File(open(f"tmp/{hashed}.png", "rb").read())

def parse_user(text):
    user = None
    if text.startswith("<@"):
        user = bot.get_user(int(text[2:-1]))
    else:
        try: user = bot.get_user(int(text))
        except: pass
    return user