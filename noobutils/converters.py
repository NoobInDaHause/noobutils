import contextlib
import discord

from redbot.core import commands

from emoji import EMOJI_DATA
from typing import Union


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    async def convert(
        self, ctx: commands.Context, argument
    ) -> Union[discord.Emoji, str, None]:
        try:
            argument = int(argument)
            return discord.utils.get(ctx.bot.emojis, id=argument)
        except ValueError:
            argument = argument.strip()
            if argument in EMOJI_DATA:
                return argument
            custom_emoji = argument.split(":")
            if len(custom_emoji) >= 2:
                custom_emoji_id = custom_emoji[2].replace(">", "")
                with contextlib.suppress(ValueError):
                    emoji_id = int(custom_emoji_id)
                    return discord.utils.get(ctx.bot.emojis, id=emoji_id)
        return None
