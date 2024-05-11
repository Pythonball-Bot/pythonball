import discord
import asyncio
from main import owner, subowners

cmds = {}
groups = []

class permissions:
    @staticmethod
    def is_owner(user : discord.Member):
        return user.id == owner
    
    @staticmethod
    def is_subowner(user : discord.Member):
        return user.id == owner or user.id in subowners
    
    @staticmethod
    def is_admin(user : discord.Member):
        return user.guild_permissions.administrator

def command(func):
    global cmds
    # print(f"length of dict: {len(cmds.keys())}")
    print(f"Registered command {func.__name__}")
    if func.__name__.lower() not in cmds.keys():
        cmds[func.__name__.lower()] = {"function": func, "permissions": []}
    def wrapper(msg, piped, args, **kwargs):
        asyncio.run(func(msg, piped, args, **kwargs))
    return wrapper

def perms(*args):
    global cmds
    def decorator(func):
        cmds[func.__name__.lower()] = {"function": func, "permissions": args}
        return func
    return decorator

def group(clas):
    global cmds, groups
    groups.append(clas.__name__.lower())
    functions = [func for func in dir(clas) if not func.startswith("__")]
    for func in functions:
        real_func = getattr(clas, func)
        cmds[f"{clas.__name__.lower()}:{func.lower()}"] = {"function": real_func, "permissions": []}
    print(f"Registered command group {clas.__name__.lower()} ({','.join(functions)})")
