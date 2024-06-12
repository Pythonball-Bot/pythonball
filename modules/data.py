import json

serverData = json.loads(open("data/servers.json").read())
def save_servers():
    try:
        open("data/servers.json", "w", encoding="utf-8").write(json.dumps(serverData, indent=1))
    except Exception as error:
        raise error
    finally: 
        open("data/servers-backup.json", "w", encoding="utf-8").write(json.dumps(serverData, indent=1))
open("data/servers-backup.json", "w", encoding="utf-8").write(json.dumps(serverData, indent=1))

class servers:
    @staticmethod
    def read(guild, query, default = None):
        if type(guild) is not int:
            guild = guild.id
        segments = query.split(".")
        if str(guild) not in serverData.keys():
            serverData[str(guild)] = {}
        currentData = serverData[str(guild)]
        for segment in segments:
            if segment not in currentData.keys():
                return default
            else: currentData = currentData[segment]
        return currentData
    
    @staticmethod
    def write(guild, query, newData):
        if type(guild) is not int:
            guild = guild.id
        segments = query.split(".")
        if str(guild) not in serverData.keys():
            serverData[str(guild)] = {}
        currentData = serverData[str(guild)]
        for i, segment in enumerate(segments):
            if segment not in currentData.keys():
                if i < len(segments) - 1:
                    currentData[segment] = {}
                    currentData = currentData[segment]
                else:
                    currentData[segment] = newData
                    break
            else:
                if i == len(segments) - 1:
                    currentData[segment] = newData
                    break
                else: currentData = currentData[segment]
        save_servers()


userData = json.loads(open("data/users.json").read())
def save_users():
    try:
        open("data/users.json", "w", encoding="utf-8").write(json.dumps(userData, indent=1))
    except Exception as error:
        raise error
    finally: 
        open("data/users-backup.json", "w", encoding="utf-8").write(json.dumps(userData, indent=1))
open("data/users-backup.json", "w", encoding="utf-8").write(json.dumps(userData, indent=1))

class users:
    @staticmethod
    def read(user, query, default = None):
        if type(user) is not int:
            user = user.id
        segments = query.split(".")
        if str(user) not in userData.keys():
            serverData[str(user)] = {}
        currentData = userData[str(user)]
        for i, segment in enumerate(segments):
            if segment not in currentData.values():
                return default
            else: currentData = currentData[segment]
        return currentData
    
    @staticmethod
    def write(user, query, newData):
        if type(user) is not int:
            user = user.id
        segments = query.split(".")
        if str(user) not in userData.keys():
            serverData[str(user)] = {}
        currentData = userData[str(user)]
        for i, segment in enumerate(segments):
            if segment not in currentData.values():
                if i < len(segments) - 1: currentData[segment] = {}
                else:
                    currentData[segment] = newData
                    return
            else:
                if i < len(segments) - 1:
                    currentData[segment] = newData
                    return
                else: currentData = currentData[segment]
        save_users()