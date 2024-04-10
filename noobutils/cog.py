import logging

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from typing import List


class Cog(commands.Cog):
    def __init__(
        self,
        bot: Red,
        cog_name: str,
        version: str,
        authors: List[str],
        use_config: bool = False,
        identifier: int = 1234567890,
        force_registration: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = (
            Config.get_conf(
                None,
                identifier=identifier,
                force_registration=force_registration,
                cog_name=cog_name,
            )
            if use_config
            else None
        )
        self.__version__ = version
        self.__author__ = authors
        self.__docs__ = f"https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/{cog_name.lower()}/README.md"
        self.log = logging.getLogger(f"red.NoobCogs.{cog_name}")

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})"
        )


class GroupCog(commands.GroupCog):
    def __init__(
        self,
        bot: Red,
        cog_name: str,
        version: str,
        authors: List[str],
        use_config: bool = False,
        identifier: int = 1234567890,
        force_registration: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = (
            Config.get_conf(
                None,
                identifier=identifier,
                force_registration=force_registration,
                cog_name=cog_name,
            )
            if use_config
            else None
        )
        self.__version__ = version
        self.__author__ = authors
        self.__docs__ = f"https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/{cog_name.lower()}/README.md"
        self.log = logging.getLogger(f"red.NoobCogs.{cog_name}")

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})"
        )
