# from main import *
# import discord

# @group
# class board:
#     async def add(msg: discord.Message, piped, args):
#         if not msg.author.guild_permissions.administrator: return
#         server_check(msg.guild.id)
#         emoji = args[0]
#         if(len(emoji) > 1):
#             await msg.channel.send("Either you forgot a space or you sent a custom emoji. Custom emoji boards aren't supported yet, until they are you have to use built in emojis.")
#             return
#         channel = args[1]
#         count = 3
#         if len(args) > 2: count = int(args[2])
#         servers[str(msg.guild.id)]["boards"][emoji] = {"channel": int(channel[2:-1]), "count": count, "messages": []}
#         save_servers()
#         await msg.channel.send(f"Added a {emoji} board to {channel}. Messages need {count} {emoji}s to get on the board.")

#     async def force(msg: discord.Message, piped, args):
#         if msg.author.guild_permissions.manage_messages is False and msg.author.id != owner:
#             await msg.channel.send("Manage Messages is required to use this command.")
#             return
        
#         server_check(msg.guild.id)
#         if len(args) == 0:
#             await msg.channel.send("Please specify a board to add the message to (with the emoji of that board)")
#             return
#         emoji = args[0]
#         message = msg.reference
#         if message is None:
#             if len(args) < 2:
#                 await msg.channel.send("Either reply to a message or add the message ID after the emoji, otherwise I don't know what message to add.")
#                 return
#             message = await msg.channel.fetch_message(int(args[1]))
#         if not emoji in servers[str(msg.guild.id)]["boards"]:
#             await msg.channel.send(f"There is no {emoji} board in the server.")
#             return
        
#         boar = servers[str(msg.guild.id)]["boards"][emoji]
#         await add_to_board(boar, message, emoji)
#         await msg.channel.send(f"Added the messgage to the {emoji} board.")


# async def add_to_board(boar, message, emoji):
#     if type(message) == discord.MessageReference:
#         message = await (bot.get_guild(message.guild_id).get_channel(message.channel_id)).fetch_message(message.message_id)

#     async with (await bot.fetch_channel(boar["channel"])).typing():
#         boar["messages"].append(message.id)
#         embed = discord.Embed(description = message.content)
#         match = re.match(r"^https:\/\/[\w\.]*\/[\w\-\/]+\.(?:png|gif)(?!\.).*", message.content)
#         if match is not None:
#             embed.set_image(url = match.string)
#         if len(message.attachments) > 0:
#             embed.set_image(url = message.attachments[0].url)
#         if message.content.startswith("https://") and "tenor.com" in message.content:
#             embed.set_image(url = message.content)
#         embed.set_author(name = message.author.name, icon_url = message.author.avatar.url)
#         embed.timestamp = message.created_at
#         number = len(message.attachments) - 1
#         embed.set_footer(text = f"+ {number} more attachment{'s' if number > 1 else ''}" if number > 0 else None)
#         file = None
#         # if not reaction.is_custom_emoji():
#         #     if not os.path.exists(f"tmp/{hash(reaction.emoji)}.png"):
#         #         image = emoji_image(reaction.emoji)
#         #         image.save(f"tmp/{hash(reaction.emoji)}.png")
#         #         file = discord.File(f"tmp/{hash(reaction.emoji)}.png", filename="thumb.png")
#         #     embed.set_thumbnail(url = "attachment://thumb.png")
#         # else:
#         #     embed.set_thumbnail(url = reaction.emoji.url)
#         await (await bot.fetch_channel(boar["channel"])).send(f"{emoji} {message.jump_url}", embed = embed)
#         save_servers()