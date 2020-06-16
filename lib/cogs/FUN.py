from discord.ext.commands import Cog, command, cooldown, BucketType
#from discord.ext.commands import commands
from discord.ext.commands import CommandOnCooldown
from discord import Embed, File, Member
import discord
import os
import datetime
import random

TIMESTAMP = datetime.datetime.utcnow()
VERSION = "0.2"

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
#----------------------------------------------------------------------------------------------------------GOOD OR BAD--
    @command(name="gorb", help='Encouraging (or discouraging) comment from MandoBot')
    @cooldown(1, 30, BucketType.user)
    async def gorb(selfself, ctx):
        gorblist = ['good', 'bad']
        gorb = random.choice(gorblist)

        if gorb == ('good'):
            grt = [f'{ctx.author.mention} is Awesome!',
                   f'We love you {ctx.author.mention}!',
                   f'I love {ctx.author.mention}']
            textresponse = random.choice(grt)
            grp = os.listdir("/home/pi/Desktop/Mandobot2/data/hellogood")
            imgpath = random.choice(grp)
            picresponse = "/home/pi/Desktop/Mandobot2/data/hellogood/" + imgpath

            embed = discord.Embed(title=' ', description=f'{textresponse} ', color=0x00ff00)
            file = discord.File(f"{picresponse}", filename=f"{picresponse}")
            embed.set_image(url=f"attachment://{picresponse}")

            await ctx.message.delete()
            await ctx.send(file=file, embed=embed)

        if gorb == ('bad'):
            brt = [f'Fuck you {ctx.author.mention}',
                   f'{ctx.author.mention} can eat my ass.',
                   f'Hey {ctx.author.mention},I just got done fucking your mom.']
            textresponse = random.choice(brt)
            brp = os.listdir("/home/pi/Desktop/Mandobot2/data/hellobad")
            imgpath = random.choice(brp)
            picresponse = "/home/pi/Desktop/Mandobot2/data/hellobad/" + imgpath

            embed = discord.Embed(title=' ', description=f'{textresponse} ', color=0x00ff00)
            file = discord.File(f"{picresponse}", filename=f"{picresponse}")
            embed.set_image(url=f"attachment://{picresponse}")

            await ctx.message.delete()
            await ctx.send(file=file, embed=embed)

    @gorb.error
    async def gorb_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            msg = 'This command is on cooldown, try again in **{:.0f}** seconds fucker'.format(error.retry_after)
            await ctx.message.delete()
            await ctx.send(msg)



# -------------------------------------------------------------------------------------------------------------THE WAY--
    @command(name="theway", help='This is the way')
    @cooldown(1, 30, BucketType.user)
    async def the_way(self, ctx):
        await ctx.message.delete()
        await ctx.send(file=File("/home/pi/Desktop/Mandobot2/data/images/thisisthegif.gif"))

# ---------------------------------------------------------------------------------------------------Random Lola Facts--
    @command(name="fact", help='Random fact about Lola')
    @cooldown(1, 30, BucketType.user)
    async def random_fact(self, ctx):
        lolafact = [
        'Age: 19',
        'Sexual Orientation: Extremely Bisexual',
        'Hair Color: Blonde',
        'Eye Color: Blue',
        'Height: 5ft 5in',
        'Weight: 125lbs',
        'Breast Size: A very perky 32B',
        'Tattoos: None, but searching for the perfect one (So help me with suggestions)',
        'Location: Undisclosed (You\'ll have to figure this out or if we meet up, you\'ll know)',
        'Piercings: Both nipples, Belly button, Ears',
        'Social Media:lolabunz80 on snapchat, lolabunz#3846 on discord',
        'Hobbies: Outdoors, hiking, cars, computers, video games, food, jetskiing, working out'
        ]
        response = random.choice(lolafact)
        await ctx.message.delete()
        await ctx.send(f'Random Lola Fact:  {response}')

# ------------------------------------------------------------------------------------------------------------Bot Info--
    @command(name='info', help='Responds with info about this bot')
    async def info(self, ctx):
        info = discord.Embed(
            title=' ',
            description=(f'MandoBot v{VERSION} created by Eros\n' 'AKA Your Daddy'),
            colour=discord.Colour.blue()
        )
        await ctx.send(embed=info)

# -----------------------------------------------------------------------------------------------------------COG READY--
    @Cog.listener()
    async def on_ready(self):
        print(f"{TIMESTAMP}: FUN COG READY")
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))