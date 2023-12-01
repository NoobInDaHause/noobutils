from __future__ import annotations

import datetime
import discord

from redbot.core import commands

from emoji import EMOJI_DATA
from rapidfuzz import process
from typing import List, Optional, Union
from unidecode import unidecode

from .exceptions import FuzzyRoleConversionFailure


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    def __init__(self, emoji: Union[discord.Emoji, str]):
        super().__init__()
        self._emoji = emoji
        self.name: str = emoji.name if isinstance(emoji, discord.Emoji) else emoji.replace(":", "")
        self.id: int = emoji.id if isinstance(emoji, discord.Emoji) else None
        self.url: str = emoji.url if isinstance(emoji, discord.Emoji) else None
        self.guild: discord.Guild = emoji.guild if isinstance(emoji, discord.Emoji) else None
        self.guild_id: int = emoji.guild_id if isinstance(emoji, discord.Emoji) else None

    @classmethod
    async def convert(
        cls, ctx: commands.Context, argument: str
    ) -> Union[discord.Emoji, str]:
        if argument.strip() in EMOJI_DATA.keys():
            return cls(emoji=argument.strip())
        else:
            return cls(emoji=await super().convert(ctx, argument.strip()))

    def __str__(self) -> str:
        return str(self._emoji)


# https://github.com/phenom4n4n/phen-cogs/blob/327fc78c66814ac01f644c6b775dc4d6db6e1e5f/roleutils/converters.py#L36
# original converter from https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/converters.py#L19
class NoobFuzzyRole(commands.RoleConverter):
    """
    This will accept role ID's, mentions, and perform a fuzzy search for
    roles within the guild and return a list of role objects
    matching partial names
    Guidance code on how to do this from:
    https://github.com/Rapptz/discord.py/blob/rewrite/discord/ext/commands/converter.py#L85
    https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/mod.py#L24
    """

    def __init__(self, role: discord.Role):
        super().__init__()
        self._role: discord.Role = role

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> NoobFuzzyRole:
        try:
            basic_role = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass
        else:
            return cls(role=basic_role)
        result = [
            (r[2], r[1])
            for r in process.extract(
                argument,
                {r: unidecode(r.name) for r in ctx.guild.roles},
                limit=None,
                score_cutoff=75,
            )
        ]
        if not result:
            raise FuzzyRoleConversionFailure(f'Role "{argument}" not found.')

        sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
        return cls(role=sorted_result[0][0])

    def __str__(self) -> str:
        return self._role.name

    def __repr__(self) -> str:
        return f'<Role id={self._role.id} name={self._role.name!r}>'

    def is_default(self) -> bool:
        return self._role.is_default()

    def is_bot_managed(self) -> bool:
        return self._role.is_bot_managed()

    def is_premium_subscriber(self) -> bool:
        return self._role.is_premium_subscriber()

    def is_integration(self) -> bool:
        return self._role.is_integration()

    def is_assignable(self) -> bool:
        return self._role.is_assignable()

    @property
    def name(self) -> str:
        return self._role.name

    @property
    def guild(self) -> discord.Guild:
        return self._role.guild

    @property
    def permissions(self) -> discord.Permissions:
        return self._role.permissions

    @property
    def colour(self) -> discord.Colour:
        return self._role.colour

    @property
    def color(self) -> discord.Color:
        return self._role.color

    @property
    def icon(self) -> Optional[discord.asset.Asset]:
        return self._role.icon

    @property
    def display_icon(self) -> Optional[Union[discord.asset.Asset, str]]:
        return self._role.display_icon

    @property
    def created_at(self) -> datetime.datetime:
        return self._role.created_at

    @property
    def mention(self) -> str:
        return self._role.mention

    @property
    def mentionable(self) -> bool:
        return self._role.mentionable

    @property
    def members(self) -> List[discord.Member]:
        return self._role.members

    @property
    def managed(self) -> bool:
        return self._role.managed

    @property
    def unicode_emoji(self) -> str:
        return self._role.unicode_emoji

    @property
    def id(self) -> int:
        return self._role.id

    async def edit(
        self,
        *,
        name: str = discord.utils.MISSING,
        permissions: discord.Permissions = discord.utils.MISSING,
        colour: Union[discord.Colour, int] = discord.utils.MISSING,
        color: Union[discord.Colour, int] = discord.utils.MISSING,
        hoist: bool = discord.utils.MISSING,
        display_icon: Optional[Union[bytes, str]] = discord.utils.MISSING,
        mentionable: bool = discord.utils.MISSING,
        position: int = discord.utils.MISSING,
        reason: Optional[str] = discord.utils.MISSING,
    ) -> Optional[discord.Role]:
        return await self._role.edit(
            name=name,
            permissions=permissions,
            colour=colour,
            color=color,
            hoist=hoist,
            display_icon=display_icon,
            mentionable=mentionable,
            position=position,
            reason=reason
        )

    async def delete(self, *, reason: Optional[str] = None) -> None:
        await self._role.delete(reason=reason)
