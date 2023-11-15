from __future__ import annotations

import discord

from redbot.core import commands

from emoji import EMOJI_DATA
from rapidfuzz import process
from typing import Union
from unidecode import unidecode

from .exceptions import FuzzyRoleConversionFailure


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    async def convert(
        self, ctx: commands.Context, argument
    ) -> Union[discord.Emoji, str]:
        if argument.strip() in EMOJI_DATA.keys():
            return argument.strip()
        else:
            return await super().convert(ctx, argument.strip())


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

    def __init__(self, response: bool = True):
        self.response = response
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            basic_role = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass
        else:
            return basic_role
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
            raise FuzzyRoleConversionFailure(
                f'Role "{argument}" not found.' if self.response else None
            )

        sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
        return sorted_result[0][0]
