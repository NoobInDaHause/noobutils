import discord

from redbot.core import commands

from emoji import EMOJI_DATA

from .exceptions import UnknownEmoji


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    async def convert(self, context: commands.Context, argument: str):
        argument = argument.strip()
        checkarg = argument.replace(":", "")
        emote = discord.utils.get(context.bot.emojis, name=checkarg)
        if emote is None:
            raise UnknownEmoji(f'Emoji "{argument}" not found.')
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(context, argument))
        else:
            return argument
