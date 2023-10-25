import discord

from redbot.core.commands import Context, EmojiConverter as ec

from emoji import EMOJI_DATA

from .exceptions import UnknownEmoji


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(ec):
    async def convert(self, ctx: Context, argument: str):
        argument = argument.strip()
        checkarg = argument.replace(":", "")
        emote = discord.utils.get(ctx.bot.emojis, name=checkarg)
        if emote is None:
            raise UnknownEmoji(f'Emoji "{argument}" not found.')
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(ctx, argument))
        else:
            return argument
