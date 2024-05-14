from main import bot, afkMessages
from modules.commands import *
import modules.helpers as helpers
import discord
import random
from pytube import YouTube
from moviepy import editor
import os

@command
async def echo(msg : discord.Message, piped, args):
    channel = msg.channel
    index = 0
    if args[0].startswith("<#"):
        index = 1
        channel = await bot.fetch_channel(args[0][2:-1])
    if piped is not None: message = piped
    else: message = " ".join(args[index:])
    await channel.send(message)

@command
async def ask(msg : discord.Message, piped, args):
    message = " ".join(args)
    if piped is not None:
        message = piped
    await msg.channel.send(message)
    return (await bot.wait_for("message", check=lambda m: m.channel == msg.channel)).content

@command
async def cwd(msg: discord.Message, piped, args):
    async with msg.channel.typing():
        emoji = await helpers.guild_emoji(msg.guild)

        await msg.channel.send(
f"""Channel: {msg.channel.mention} : {msg.channel.id}
User: {msg.author.mention} : {msg.author.id}
Server: <:{msg.guild.id}:{emoji.id}> {msg.guild.name} : {msg.guild.id}
Message: {msg.jump_url} : {msg.id}""")
        
        await bot.get_guild(717048644708073534).delete_emoji(emoji)

@command
async def download(msg: discord.Message, piped, args):
    if len(args) == 0:
        await msg.channel.send("ADD LINK ICANT BE BOTHERED TO POUT EFFORT INTO THIS")
        return
    video = YouTube(args[0])
    if video.length > 60 * 15:
        await msg.channel.send("15 minute video length limit why? cause its an arbitrary limit i set")
        return
    async with msg.channel.typing():
        stream = video.streams.filter(progressive=True).first()
        path = stream.default_filename
        stream.download("tmp")
        video = editor.VideoFileClip(f"tmp/{path}")
        video.audio.write_audiofile(f"tmp/{path}.mp3")
        await msg.channel.send(file=discord.File(open(f"tmp/{path}.mp3", "rb")))
        os.remove(f"tmp/{path}")
        os.remove(f"tmp/{path}.mp3")

@command
async def afk(msg: discord.Message, piped, args):
    afkMessage = f"**{msg.author.name}** is afk"
    if len(args) > 0:
        afkMessage += f": {' '.join(args)}"
    afkMessages.append({"user": msg.author.id,"server": msg.guild.id, "message": afkMessage})
    await msg.channel.send(f"bye bye")

@command
async def roll(msg: discord.Message, piped, args):
    if len(args) == 0:
        await msg.channel.send("please provide a query for the dice")
        return

    query = args[0]
    try: sides, dice_count, hit_criteria, hit_value = parse_dice_query(query.lower().replace(" ", ""))
    except:
        await msg.channel.send("failed to parse query. make sure you did it right")
        return
    
    message = ""
    current_row = 0
    hit_count = 0
    total = 0
    for dice in range(dice_count):
        if current_row >= 6:
            message += "\n"
            current_row = 0
        
        result = random.randrange(1, sides)
        total += result
        if hit_criteria == "<" and result < hit_value: hit_count += 1
        if hit_criteria == ">" and result > hit_value: hit_count += 1
        if hit_criteria == "=" and result == hit_value: hit_count += 1

        message += f"[ **{result}** ]"
        current_row += 1
    message = message.strip("\n")

    if dice_count > 1:
        message += "\n\n"
        if hit_criteria != None: message += f"Hits  **{hit_count}**\n"
        message += f"Total  **{total}**"

    await msg.channel.send(message)
    
def parse_dice_query(query):
    sides = 1
    dice_count = 1
    hit_criteria = None
    hit_value = 0

    current = ""
    for character in query:
        if character == "d":
            if current != "":
                dice_count = int(current)
                current = ""
            continue

        if character in "<>=":
            sides = int(current)
            current = ""
            hit_criteria = character

        current += character
    
    if hit_criteria == None:
        sides = int(current)
    else: hit_value = int(current)

    return sides, dice_count, hit_criteria, hit_value

@group
class dev:
    # @perms(permissions.is_owner)
    async def guilds(msg: discord.Message, piped, args):
        for guild in bot.guilds:
            async with msg.channel.typing():
                emoji = await helpers.guild_emoji(guild)

                await msg.channel.send(f"<:{guild.id}:{emoji.id}> {guild.name} : {guild.id}")
                
                await bot.get_guild(717048644708073534).delete_emoji(emoji)
