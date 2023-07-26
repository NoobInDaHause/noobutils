from redbot.core import commands

from emoji import EMOJI_DATA

class NoobCoordinate(dict):
    def __convert__(self, key):
        return key

class NoobEmojiConverter(commands.EmojiConverter):
    async def convert(self, context: commands.Context, argument: str):
        argument = argument.strip()
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(context=context, argument=argument))
        else:
            return argument
