# ====================================================SETUP==============================================================
# ---------------------------------------------------IMPORTS-------------------------------------------------------------
import datetime
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from ..db import db

# ---------------------------------------------------CONSTANTS-----------------------------------------------------------
PREFIX = "$"
OWNER_IDS = [523295657381855235]
GUILD_ID = 721441377627406467
BOT_CHANNEL = 721504513881669644
NOTIFY_CHANNEL = 721461125723717633
BOT_NAME = 'MANDOBOT'
TIMESTAMP = datetime.datetime.utcnow()

# ------------------------------------------------COG FILE FINDER--------------------------------------------------------
print(f'{TIMESTAMP}: SEARCHING FOR COGS')
COG_DIR = os.listdir(f'/home/pi/Desktop/Mandobot2/lib/cogs')
COGLIST = []
for names in COG_DIR:
    if names.endswith(".py"):
        COGLIST.append(names)
COGS = [os.path.splitext(x)[0] for x in COGLIST]
print(f'{TIMESTAMP}: SEARCH COMPLETED')
print(f'{TIMESTAMP}: COGS DISCOVERED: {COGS}')


# -----------------------------------------------------READY-------------------------------------------------------------
class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


# ------------------------------------------------------BOT--------------------------------------------------------------
class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f'{TIMESTAMP}: {cog} COG LOADED ')

        print(f'{TIMESTAMP}: SETUP COMPLETED')

    def run(self, version):
        self.VERSION = version

        print(f'{TIMESTAMP}: RUNNING SETUP')
        self.setup()

        with open("/home/pi/Desktop/Mandobot2/lib/bot/token", "r", encoding="utf=8") as tf:
            self.TOKEN = tf.read()

        print(f"{TIMESTAMP}: BOT STARTING")
        super().run(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        await self.notifyout.send(f'Read the rules you sum\'bitches.')

    async def on_connect(self):
        print(f"{TIMESTAMP}: BOT CONNECTED")

    async def on_disconnect(self):
        print(f"{TIMESTAMP}: BOT DISCONNECTED")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await self.stdout.send(f"{TIMESTAMP}: A command error occured")

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif hasattr(exc, "original"):
            raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(GUILD_ID)
            self.stdout = self.get_channel(BOT_CHANNEL)
            self.notifyout = self.get_channel(NOTIFY_CHANNEL)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(hour=12))
            self.scheduler.start()

            # channel = self.get_channel(720232237920026624)
            # await self.stdout.send("Now Online!")

            # embed = Embed(
            #     title="MandoBot is now Online",
            #     description="This is the way."
            # )
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to the other one", True),
            #           ("A non-inline field", "This field will appear on it's own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # #embed.set_author(name="MandoBot is now Online", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer!")
            # await channel.send(embed=embed)
            # await channel.send(file=File("/home/pi/Desktop/Mandobot2.0/data/images/mandobot4.jpg"))

            print(f"{TIMESTAMP}: {BOT_NAME} READY. THIS IS THE WAY.")

        else:
            print(f"{TIMESTAMP}: BOT RECONNECTED")

    async def on_message(self, message):
        if not message.author.bot and message.author != message.guild.me:
            await self.process_commands(message)


# ------------------------------------------------------END--------------------------------------------------------------
bot = Bot()
