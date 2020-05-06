import discord

class BotClient(discord.Client):
    async def on_ready(self):
        print("[INFO] Logged on as [{}]".format(self.user))

    async def on_message(self, message):
        print("[INFO] Message from {0.author}: {0.content}".format(message))

