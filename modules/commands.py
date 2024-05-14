import discord
import asyncio

commands = {"functions": {}, "permissions": {}}
groups = []

owner = 663186731725488138
subowners = [993927156142981240, 993927897477828790]

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
    name = func.__qualname__.lower()
    print(f"Registered command {name}")
    commands["functions"][name] = func
    def wrapper(msg, piped, args, **kwargs):
        asyncio.run(func(msg, piped, args, **kwargs))
    return wrapper

def perms(func, *args):
    name = func.__qualname__.lower()
    commands["permissions"][name] = args
    return func

def group(clas):
    groups.append(clas.__name__.lower())
    functions = [func for func in dir(clas) if not func.startswith("__")]
    for func in functions:
        real_func = getattr(clas, func)
        commands["functions"][real_func.__qualname__] = real_func
    print(f"Registered command group {clas.__name__.lower()} ({','.join(functions)})")