from redbot.core.commands import Context, EmojiConverter as ec

from emoji import EMOJI_DATA


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(ec):
    async def convert(self, context: Context, argument: str):
        argument = argument.strip()
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(context, argument))
        else:
            return argument
