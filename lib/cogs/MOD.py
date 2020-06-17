from datetime import datetime, timedelta
from typing import Optional
from asyncio import sleep
from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions
from lib.db import db

MUTE_ROLE = 721461036640894986  # DUNCE
TIMESTAMP = datetime.utcnow()


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------------------------------------------------------------------------------MEMBER KICK--
    @command(name="kick", help='Kicks Member. [cmd, @member, reason]')
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)

                    embed = Embed(title="Member kicked",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
                              ("Actioned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")

            await ctx.send("Action complete.")

    @kick_members.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    # ------------------------------------------------------------------------------------------------------MEMBER BAN--
    @command(name="ban", help='Bans Member. [cmd, @member, reason]')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(title="Member banned",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
                              ("Actioned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be banned.")

            await ctx.send("Audios Mother Fucker.")

    @ban_members.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    # ---------------------------------------------------------------------------------------------------MESSAGE PURGE--
    @command(name="clear", aliases=["purge"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow() - timedelta(days=14),
                                                  check=_check)

                await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

        else:
            await ctx.send("The limit provided is not within acceptable bounds.")

    # ----------------------------------------------------------------------------------------------------MUTE SETUP--
    async def mute_members(self, message, targets, hours, reason):
        unmutes = []

        for target in targets:
            if not self.mute_role in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    role_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None

                    db.execute("INSERT INTO mutes VALUES (?, ?, ?)",
                               target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                    await target.edit(roles=[self.mute_role])

                    embed = Embed(title="Member muted",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", target.display_name, False),
                              ("Actioned by", message.author.display_name, False),
                              ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    await self.log_channel.send(embed=embed)

                    if hours:
                        unmutes.append(target)

        return unmutes

    # ----------------------------------------------------------------------------------------------------MEMBER MUTE--

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def mute_command(self, ctx, targets: Greedy[Member], hours: Optional[int], *,
                           reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            unmutes = await self.mute_members(ctx.message, targets, hours, reason)
            await ctx.send("Action complete.")

            if len(unmutes):
                await sleep(hours)
                await self.unmute_members(ctx.guild, targets)


    @mute_command.error
    async def mute_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    # ----------------------------------------------------------------------------------------------------UNMUTE SETUP--
    async def unmute_members(self, guild, targets, *, reason="Mute time expired."):
        for target in targets:
            if self.mute_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
                roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if role_ids and len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

                await target.edit(roles=roles)

                embed = Embed(title="Member unmuted",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", target.display_name, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)
            
    # ----------------------------------------------------------------------------------------------------MEMBER UNMUTE-
    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("One or more required arguments is missing.")

        else:
            await self.unmute_members(ctx.guild, targets, reason=reason)

    @unmute_command.error
    async def unmute_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    # -------------------------------------------------------------------------------------------------------COG READY--
    @Cog.listener()
    async def on_ready(self):
        print(f"{TIMESTAMP}: MOD COG READY")
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(721461111647502407)
            self.mute_role = self.bot.guild.get_role(721461036640894986)
            self.bot.cogs_ready.ready_up("mod")


def setup(bot):
    bot.add_cog(Mod(bot))

