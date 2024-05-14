import discord
import asyncio
import os
from PIL import Image
import re
import modules.data
from modules.commands import commands, groups

os.system("clear")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents = intents)

# testy = bot.get_guild(717048644708073534)

afkMessages = []

@bot.event
async def on_message(msg : discord.Message):
    if(msg.content == ""
       or msg.author == bot.user):
        return
    
    for i, afkMessage in enumerate(afkMessages):
        if msg.author.id == afkMessage["user"]:
            await msg.channel.send("hi welcome back")
            afkMessages.pop(i)
            break
    
    for mention in msg.mentions:
        for i, afkMessage in enumerate(afkMessages):
            if msg.guild.id != afkMessage["server"]: continue
            if mention.id != afkMessage["user"]: continue
            await msg.channel.send(afkMessage["message"])

    if not msg.content.startswith(";"): return

    words = msg.content[1:].split(" ")
    cmd = ""
    args = []
    index = 0
    out = None
    error = False

    for word in words:
        if len(word) == 0 or word == " ":
            continue

        if cmd == "":
            cmd = word.lower()
        elif word != "|":
            args.append(word)

        index += 1

        if index == len(words) or word == "|":
            if cmd.lower() in groups:
                cmd = f"{cmd}.{args[0].lower()}"
                args.pop(0)
            if not cmd in commands:
                error = True
                break
            try:
                for perm in commands[cmd.lower()]["permissions"]:
                    if not perm(msg.author):
                        await msg.channel.send(f"Missing required permission: {perm.__name__}")
                        break
                out = await commands[cmd.lower()](msg, out, args)
            except IndexError:
                await msg.channel.send("Missing required paramters.")
                await msg.add_reaction("🚫")
            args = []
            cmd = ""

    if error:
        await msg.channel.send("That is not a command fool.")

# @bot.event
# async def on_reaction_add(reaction : discord.Reaction, user : discord.Member):
#     server = user.guild.id
#     server_check(server)
#     if reaction.emoji in servers[str(server)]["boards"].keys():
#         boar = servers[str(server)]["boards"][reaction.emoji]
#         if reaction.count >= boar["count"]:
#             if not reaction.message.id in boar["messages"]:
#                 await add_to_board(boar, reaction.message, reaction.emoji)


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


@group
class dev:
    async def guilds(msg: discord.Message, piped, args):
        if not msg.author.id == 663186731725488138: return
        for guild in bot.guilds:
            async with msg.channel.typing():
                emoji = await guild_emoji(guild)

                await msg.channel.send(f"<:{guild.id}:{emoji.id}> {guild.name} : {guild.id}")
                
                await bot.get_guild(717048644708073534).delete_emoji(emoji)

bot.run(open("SECRET/token").read())