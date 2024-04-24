import discord
import asyncio
import os
from PIL import Image
import json
import base64
import io
import requests
import re
from pytube import YouTube
from moviepy import editor
import random
import datetime
from better_profanity import profanity

profanity.load_censor_words(whitelist_words=["crap", "rum", "rump", "ugly", "undies", "unwed", "urinal", "urine", "piss", "trashy", "transsexual", "drunk", "douchey", "duche", "yaoi", "yury", "woody", "vodka", "vomit", "voyeur", "uzi", "ugly", "twat", "twathead", "twats", "twatty", "twunt", "twunter", "sumofabiatch", "snatch", "sniper"])

aprilFools = json.loads(open("fools.json").read())
aprilFoolsThresholdRole = int(aprilFools["role"])
aprilFoolsChannelNames = aprilFools["names"]
aprilFoolsChannelEdits = aprilFools["edits"]
aprilFoolsNuclearOption = aprilFools["nuclear"]

servers = json.loads(open("servers.json").read())
def save_servers():
    try:
        open("servers.json", "w", encoding="utf-8").write(json.dumps(servers, indent=1))
    except Exception as error:
        raise error
    finally: 
        open("servers-backup.json", "w", encoding="utf-8").write(json.dumps(servers, indent=1))
open("servers-backup.json", "w", encoding="utf-8").write(json.dumps(servers, indent=1))

users = json.loads(open("users.json").read())
def save_users():
    try:
        open("users.json", "w", encoding="utf-8").write(json.dumps(users, indent=1))
    except Exception as error:
        raise error
    finally: 
        open("users-backup.json", "w", encoding="utf-8").write(json.dumps(users, indent=1))
open("users-backup.json", "w", encoding="utf-8").write(json.dumps(users, indent=1))

database = json.loads(open("db.json").read())
save_db = lambda: open("db.json", "w", encoding="utf-8").write(json.dumps(database))


owner = 663186731725488138
subowners = [993927156142981240]


afkMessages = []


os.system("clear")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents = intents)

# testy = bot.get_guild(717048644708073534)

#region command prep crap

commands = {}
groups = []

def command(func):
    print(f"Registered command {func.__name__}")
    commands[func.__name__.lower()] = func
    def wrapper(msg, piped, args, **kwargs):
        asyncio.run(func(msg, piped, args, **kwargs))
    return wrapper

def group(clas):
    groups.append(clas.__name__.lower())
    functions = [func for func in dir(clas) if not func.startswith("__")]
    for func in functions:
        real_func = getattr(clas, func)
        commands[f"{clas.__name__.lower()}:{func.lower()}"] = real_func
    print(f"Registered command group {clas.__name__.lower()} ({','.join(functions)})")

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
                cmd = f"{cmd}:{args[0].lower()}"
                args.pop(0)
            if not cmd in commands:
                error = True
                break
            try:
                out = await commands[cmd.lower()](msg, out, args)
            except IndexError:
                await msg.channel.send("Missing required paramters.")
                await msg.add_reaction("🚫")
            args = []
            cmd = ""

    if error:
        await msg.channel.send("That is not a command fool.")

async def add_to_board(boar, message, emoji):
    if type(message) == discord.MessageReference:
        message = await (bot.get_guild(message.guild_id).get_channel(message.channel_id)).fetch_message(message.message_id)

    async with (await bot.fetch_channel(boar["channel"])).typing():
        boar["messages"].append(message.id)
        embed = discord.Embed(description = message.content)
        match = re.match(r"^https:\/\/[\w\.]*\/[\w\-\/]+\.(?:png|gif)(?!\.).*", message.content)
        if match is not None:
            embed.set_image(url = match.string)
        if len(message.attachments) > 0:
            embed.set_image(url = message.attachments[0].url)
        if message.content.startswith("https://") and "tenor.com" in message.content:
            embed.set_image(url = message.content)
        embed.set_author(name = message.author.name, icon_url = message.author.avatar.url)
        embed.timestamp = message.created_at
        number = len(message.attachments) - 1
        embed.set_footer(text = f"+ {number} more attachment{'s' if number > 1 else ''}" if number > 0 else None)
        file = None
        # if not reaction.is_custom_emoji():
        #     if not os.path.exists(f"tmp/{hash(reaction.emoji)}.png"):
        #         image = emoji_image(reaction.emoji)
        #         image.save(f"tmp/{hash(reaction.emoji)}.png")
        #         file = discord.File(f"tmp/{hash(reaction.emoji)}.png", filename="thumb.png")
        #     embed.set_thumbnail(url = "attachment://thumb.png")
        # else:
        #     embed.set_thumbnail(url = reaction.emoji.url)
        await (await bot.fetch_channel(boar["channel"])).send(f"{emoji} {message.jump_url}", embed = embed)
        save_servers()

@bot.event
async def on_reaction_add(reaction : discord.Reaction, user : discord.Member):
    server = user.guild.id
    server_check(server)
    if reaction.emoji in servers[str(server)]["boards"].keys():
        boar = servers[str(server)]["boards"][reaction.emoji]
        if reaction.count >= boar["count"]:
            if not reaction.message.id in boar["messages"]:
                await add_to_board(boar, reaction.message, reaction.emoji)

#endregion

#region other crap

# i stoled this
def emoji_image(emoji):
    print(emoji)
    data = requests.get('https://unicode.org/emoji/charts/full-emoji-list.html').text
    html_search_string = r"<img alt='{}' class='imga' src='data:image/png;base64,([^']+)'>"
    matchlist = re.findall(html_search_string.format(emoji), data)
    png = matchlist[5]
    print(png)
    buffer = io.BytesIO(base64.decode(png))
    return Image.open(buffer)

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

def server_check(id):
    server_dict =  {
        "boards": {}
        }
    if not str(id) in servers.keys():
        servers[str(id)] = server_dict
    else:
        for key, value in server_dict.items():
            if key not in servers[str(id)]:
                servers[str(id)][key] = value
    save_servers()

def user_check(id):
    user_dict =  {
        "renicoins": 0,
        "foolsEdits": 0
        }
    if not str(id) in users.keys():
        users[str(id)] = user_dict
    else:
        for key, value in user_dict.items():
            if key not in users[str(id)]:
                users[str(id)][key] = value
    save_users()

def parse_user(text):
    user = None
    if text.startswith("<@"):
        user = bot.get_user(int(text[2:-1]))
    else:
        try: user = bot.get_user(int(text))
        except: pass
    return user

#endregion

@command
async def echo(msg : discord.Message, piped, args):
    channel = msg.channel
    index = 0
    if args[0].startswith("<#"):
        index = 1
        channel = await bot.fetch_channel(args[0][2:-1])
    message = " ".join(args[index:])
    if piped is not None:
        message = piped
    await channel.send(message)
    
@command
async def ask(msg : discord.Message, piped, args):
    message = " ".join(args)
    if piped is not None:
        message = piped
    await msg.channel.send(message)
    return (await bot.wait_for("message", check=lambda m: m.channel == msg.channel)).content

# @command
# async def icon(msg : discord.Message, piped, args):
#     ico = None
#     if(args)

@command
async def cwd(msg: discord.Message, piped, args):
    async with msg.channel.typing():
        emoji = await guild_emoji(msg.guild)

        await msg.channel.send(
f"""Channel: {msg.channel.mention} : {msg.channel.id}
User: {msg.author.mention} : {msg.author.id}
Server: <:{msg.guild.id}:{emoji.id}> {msg.guild.name} : {msg.guild.id}
Message: {msg.jump_url} : {msg.id}""")
        
        await bot.get_guild(717048644708073534).delete_emoji(emoji)

# @group
# class db:
#     # async def __search_db(query):


#     async def entry(msg: discord.Message, piped, args):


@group
class dev:
    async def guilds(msg: discord.Message, piped, args):
        if not msg.author.id == 663186731725488138: return
        for guild in bot.guilds:
            async with msg.channel.typing():
                emoji = await guild_emoji(guild)

                await msg.channel.send(f"<:{guild.id}:{emoji.id}> {guild.name} : {guild.id}")
                
                await bot.get_guild(717048644708073534).delete_emoji(emoji)

@group
class mod:
    # members with role
    async def mwr(msg: discord.Message, piped, args):
        async with msg.channel.typing():
            role = msg.guild.get_role(int(args[0]))
            members = msg.guild.fetch_members()
            count = [role in member.roles async for member in members].count(True)
            await msg.channel.send(f"{count} members with the {role.name} : {role.id} role in this server.")

@group
class board:
    async def add(msg: discord.Message, piped, args):
        if not msg.author.guild_permissions.administrator: return
        server_check(msg.guild.id)
        emoji = args[0]
        if(len(emoji) > 1):
            await msg.channel.send("Either you forgot a space or you sent a custom emoji. Custom emoji boards aren't supported yet, until they are you have to use built in emojis.")
            return
        channel = args[1]
        count = 3
        if len(args) > 2: count = int(args[2])
        servers[str(msg.guild.id)]["boards"][emoji] = {"channel": int(channel[2:-1]), "count": count, "messages": []}
        save_servers()
        await msg.channel.send(f"Added a {emoji} board to {channel}. Messages need {count} {emoji}s to get on the board.")

    async def force(msg: discord.Message, piped, args):
        if msg.author.guild_permissions.manage_messages is False and msg.author.id != owner:
            await msg.channel.send("Manage Messages is required to use this command.")
            return
        
        server_check(msg.guild.id)
        if len(args) == 0:
            await msg.channel.send("Please specify a board to add the message to (with the emoji of that board)")
            return
        emoji = args[0]
        message = msg.reference
        if message is None:
            if len(args) < 2:
                await msg.channel.send("Either reply to a message or add the message ID after the emoji, otherwise I don't know what message to add.")
                return
            message = await msg.channel.fetch_message(int(args[1]))
        if not emoji in servers[str(msg.guild.id)]["boards"]:
            await msg.channel.send(f"There is no {emoji} board in the server.")
            return
        
        boar = servers[str(msg.guild.id)]["boards"][emoji]
        await add_to_board(boar, message, emoji)
        await msg.channel.send(f"Added the messgage to the {emoji} board.")

@group
class coins:
    async def set(msg: discord.Message, piped, args):
        if not msg.author.id in subowners and not msg.author.id == owner:
            await msg.channel.send("Bot Owner or Bot Subowner is required to use this command.")
            return
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        if len(args) == 1:
            await msg.channel.send("Please provide a renicoin amount.")
            return
        user = parse_user(args[0])
        number = int(args[1])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        user_check(user.id)
        users[str(user.id)]["renicoins"] = number
        save_users()
        await msg.channel.send(f"Set **{user.display_name}**'s renicoin balance to {number}")

    async def add(msg: discord.Message, piped, args):
        if not msg.author.id in subowners and not msg.author.id == owner:
            await msg.channel.send("Bot Owner or Bot Subowner is required to use this command.")
            return
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        if len(args) == 1:
            await msg.channel.send("Please provide a renicoin amount.")
            return
        user = parse_user(args[0])
        number = int(args[1])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        user_check(user.id)
        users[str(user.id)]["renicoins"] += number
        save_users()
        await msg.channel.send(f"Set **{user.display_name}**'s renicoin balance to {users[str(user.id)]['renicoins']}")

    async def subtract(msg: discord.Message, piped, args):
        if not msg.author.id in subowners and not msg.author.id == owner:
            await msg.channel.send("Bot Owner or Bot Subowner is required to use this command.")
            return
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        if len(args) == 1:
            await msg.channel.send("Please provide a renicoin amount.")
            return
        user = parse_user(args[0])
        number = int(args[1])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        user_check(user.id)
        users[str(user.id)]["renicoins"] -= number
        save_users()
        await msg.channel.send(f"Set **{user.display_name}**'s renicoin balance to {users[str(user.id)]['renicoins']}")

    async def get(msg: discord.Message, piped, args):
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        user = parse_user(args[0])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        user_check(user.id)
        await msg.channel.send(f"**{user.display_name}** has {users[str(user.id)]['renicoins']} renicoins.")

@command
async def download(msg: discord.Message, piped, args):
    if len(args) == 0:
        await msg.channel.send("ADD LINK ICANT BE BOTHERED TO POUT EFFORT INTO THIS")
        return
    video = YouTube(args[0])
    if video.length > 60 * 8:
        await msg.channel.send("8 minute video length limit why? cause its an arbitrary limit i set")
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
class fools:
    async def rename(msg: discord.Message, piped, args):
        global aprilFoolsThresholdRole

        if aprilFoolsNuclearOption:
            await msg.channel.send("april fools is in nuclear lockdown mode")
            return

        if type(aprilFoolsThresholdRole) is int or aprilFoolsThresholdRole is None:
            try: aprilFoolsThresholdRole = msg.guild.get_role(aprilFoolsThresholdRole)
            except:
                msg.channel.send("the threshold role literally doesnt exist in this server")
                return
        if aprilFoolsThresholdRole not in msg.author.roles:
            await msg.channel.send(f"sorry you dont qualify to be goofy, you need {aprilFoolsThresholdRole.name} or higher")
            return
        if len(args) < 1:
            await msg.channel.send("you need a name silly")
            return
        name = "-".join(args[0:])
        name = profanity.censor(name, "█")
        channel = msg.channel
        if str(channel.id) not in aprilFoolsChannelNames.keys():
            aprilFoolsChannelNames[str(channel.id)] = channel.name
            aprilFools["names"][str(channel.id)] = channel.name
            open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        if str(channel.id) in aprilFoolsChannelEdits.keys():
            secondsSinceEdit = (datetime.datetime.now() - datetime.datetime.fromisoformat(aprilFoolsChannelEdits[str(channel.id)])).seconds
            if secondsSinceEdit < 600:
                await msg.channel.send(f"this channel is still on rename cooldown\nplease wait {round(10 - secondsSinceEdit / 60, 1)} minutes")
                return
        aprilFoolsChannelEdits[str(channel.id)] = datetime.datetime.now().isoformat()
        open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        await msg.channel.send(f"renamed **{channel.name}** to **{name}**")
        user_check(msg.author.id)
        users[str(msg.author.id)]["foolsEdits"] += 1
        save_users()
        await channel.edit(name=name)
    
    async def renametwo(msg: discord.Message, piped, args):
        # if not msg.author.id in subowners and not msg.author.id == owner:
        #     await msg.channel.send("not enough permissions to run this command")
        #     return
        global aprilFoolsThresholdRole
        if type(aprilFoolsThresholdRole) is int:
            try: aprilFoolsThresholdRole = msg.guild.get_role(aprilFoolsThresholdRole)
            except:
                msg.channel.send("the threshold role literally doesnt exist in this server")
                return
        if aprilFoolsThresholdRole not in msg.author.roles:
            await msg.channel.send(f"sorry you dont qualify to be goofy, you need {aprilFoolsThresholdRole.name} or higher")
            return
        if len(args) < 2:
            await msg.channel.send("you need two arguments silly")
            return
        name = "-".join(args[1:])
        channel = None
        try: channel = msg.guild.get_channel(int(args[0][2:-1]))
        except:
            await msg.channel.send("thats not a valid channel")
            return
        if str(channel.id) not in aprilFoolsChannelNames.keys():
            aprilFoolsChannelNames[channel.id] = channel.name
            aprilFools["names"][str(channel.id)] = channel.name
            open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        if str(channel.id) in aprilFoolsChannelEdits.keys():
            secondsSinceEdit = (datetime.datetime.now() - datetime.datetime.fromisoformat(aprilFoolsChannelEdits[str(channel.id)])).seconds
            if secondsSinceEdit < 600:
                await msg.channel.send(f"this channel is still on rename cooldown\nplease wait {round(10 - secondsSinceEdit / 60, 1)} minutes")
                return
        aprilFoolsChannelEdits[str(channel.id)] = datetime.datetime.now().isoformat()
        open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        await msg.channel.send(f"renamed **{channel.name}** to **{name}**")
        user_check(msg.author.id)
        users[str(msg.author.id)]["foolsEdits"] += 1
        save_users()
        await channel.edit(name=name)

    async def whatis(msg: discord.Message, piped, args):
        if aprilFoolsNuclearOption:
            await msg.channel.send("april fools is in nuclear lockdown mode")
            return

        if str(msg.channel.id) in aprilFools["names"]:
            await msg.channel.send(f"this channel was originally called **{aprilFools['names'][str(msg.channel.id)]}**")
        else:
            await msg.channel.send("this channel hasnt been renamed")

    async def role(msg: discord.Message, piped, args):
        global aprilFoolsThresholdRole
        if not msg.author.id in subowners and not msg.author.id == owner:
            await msg.channel.send("not enough permissions to run this command")
            return
        role = None
        try: role = msg.guild.get_role(int(args[0]))
        except:
            await msg.channel.send("please send the id of the role")
            return
        aprilFoolsThresholdRole = role
        aprilFools["role"] = role.id
        open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        await msg.channel.send(f"set the threshold role to {role.name}")

    async def revert(msg: discord.Message, piped, args):
        if not msg.author.id in subowners and not msg.author.id == owner:
            await msg.channel.send("not enough permissions to run this command")
            return
        await msg.channel.send("alr gimme a second")
        count = 0
        async with msg.channel.typing():
            for channel in msg.guild.channels:
                if str(channel.id) in aprilFoolsChannelNames.keys():
                    if channel.name != aprilFoolsChannelNames[str(channel.id)]:
                        await channel.edit(name = aprilFoolsChannelNames[str(channel.id)])
                        count += 1
        await msg.channel.send(f"reverted {count} channel to their correct names")

    async def nuclear(msg: discord.Message, piped, args):
        global aprilFoolsNuclearOption
        aprilFoolsNuclearOption = not aprilFoolsNuclearOption
        aprilFools["nuclear"] = aprilFoolsNuclearOption
        open("fools.json", "w", encoding="utf-8").write(json.dumps(aprilFools, indent=1))
        await msg.channel.send(f"{'dis' if not aprilFoolsNuclearOption else ''}engaged nuclear lockdown mode")

    async def leaderboard(msg: discord.Message, piped, args):
        edits = []
        for id, user in users.items():
            if "foolsEdits" not in user.keys(): continue
            edits.append([id, user["foolsEdits"]])
        edits.sort(key=lambda i: i[1], reverse=True)
        message = ""
        for i, edit in enumerate(edits[0:9]):
            message += f"\n{i}. **{msg.guild.get_member(int(edit[0])).name}** - {edit[1]} edits"
        await msg.channel.send(f"## top goofballs{message}")

bot.run(open("SECRET/token").read())