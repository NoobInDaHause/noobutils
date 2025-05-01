import contextlib
import logging

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from typing import Literal

from . import CogLoadError, __version__ as __nu_version__


class Cog(commands.Cog):
    def __init__(
        self,
        bot: Red,
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
                cog_name=self.__class__.__name__,
            )
            if use_config
            else None
        )
        self.log = logging.getLogger(f"red.NoobCogs.{self.__class__.__name__}")

    @property
    def utils_version(self) -> str:
        return __nu_version__  # This is temporary for now.

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    def format_help_for_context(self, context: commands.Context) -> str:
        try:
            authors = getattr(self, "__authors__")
            version = getattr(self, "__version__")
        except AttributeError as e:
            raise CogLoadError(
                "'__authors__' and '__version__' attributes are required from the cog."
            ) from e

        plural = "s" if len(authors) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{version}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in authors])}\n"
            f"Utils Version: **{self.utils_version}**"
        )

    async def cog_load(self):
        with contextlib.suppress(RuntimeError):
            self.bot.add_dev_env_value(self.__class__.__name__.lower(), lambda _: self)

    async def cog_unload(self):
        with contextlib.suppress(RuntimeError):
            self.bot.remove_dev_env_value(self.__class__.__name__.lower())


class GroupCog(commands.GroupCog):
    def __init__(
        self,
        bot: Red,
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
                cog_name=self.__class__.__name__,
            )
            if use_config
            else None
        )
        self.log = logging.getLogger(f"red.NoobCogs.{self.__class__.__name__}")

    @property
    def utils_version(self) -> str:
        return __nu_version__  # This is temporary for now.

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    def format_help_for_context(self, context: commands.Context) -> str:
        try:
            authors = getattr(self, "__authors__")
            version = getattr(self, "__version__")
        except AttributeError as e:
            raise CogLoadError(
                "'__authors__' and '__version__' attributes are required from the cog."
            ) from e

        plural = "s" if len(authors) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{version}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in authors])}\n"
            f"Utils Version: **{self.utils_version}**"
        )

    async def cog_load(self):
        with contextlib.suppress(RuntimeError):
            self.bot.add_dev_env_value(self.__class__.__name__.lower(), lambda _: self)

    async def cog_unload(self):
        with contextlib.suppress(RuntimeError):
            self.bot.remove_dev_env_value(self.__class__.__name__.lower())
