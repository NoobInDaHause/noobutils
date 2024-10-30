from __future__ import annotations

import contextlib
import discord

from redbot.core.bot import commands, Red
from redbot.core.utils import chat_formatting as cf

from typing import Dict, Union, List, Any, Union, Self

from .utility import get_button_colour, access_denied
from .exceptions import NoContextOrInteractionFound


class NoobView(discord.ui.View):
    children: List[discord.ui.Button[Self]]

    def __init__(
        self,
        *,
        obj: Union[commands.Context, discord.Interaction[Red]],
        timeout_message: str = None,
        remove_embed_on_timeout: bool = False,
        access_denied_as_video: bool = True,
        is_ephemeral: bool = False,
        timeout: float = 180,
    ):
        super().__init__(timeout=timeout)
        ctx = isinstance(obj, commands.Context)
        self.context: commands.Context = obj if ctx else None
        self.interaction: discord.Interaction[Red] = None if ctx else obj
        self.message: discord.Message = None
        self.ephemeral = is_ephemeral
        self.timeout_message = timeout_message
        self.remove_embed_on_timeout = remove_embed_on_timeout
        self.access_denied_as_video = access_denied_as_video

    async def start(self) -> Any:
        pass

    def stop(self) -> None:
        self.context = None
        self.interaction = None
        self.message = None
        return super().stop()

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if self.ephemeral and self.interaction:
            return True
        if not interaction.user:
            return True
        if await interaction.client.is_owner(interaction.user):
            return True
        if self.context and (self.context.author.id == interaction.user.id):
            return True
        if self.interaction and (self.interaction.user.id == interaction.user.id):
            return True
        await interaction.response.send_message(
            content=access_denied(not self.access_denied_as_video), ephemeral=True
        )
        return False

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        with contextlib.suppress(discord.errors.HTTPException):
            await self.message.edit()
            await self.message.edit(
                content=self.timeout_message or discord.utils.MISSING,
                embed=None if self.remove_embed_on_timeout else discord.utils.MISSING,
                view=self,
            )


class PageModal(discord.ui.Modal):
    def __init__(self, timeout: float = 30.0) -> None:
        super().__init__(title="Go To Page.", timeout=timeout)

    page = discord.ui.TextInput(min_length=1, label="Input a number.")

    async def on_submit(self, interaction: discord.Interaction[Red]):
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(
            content=f"Something went wrong. Please report this to the bot owner.\n{cf.box(str(error))}",
            ephemeral=True,
        )


class SelectPageButton(discord.ui.Button):
    view: "NoobPaginator"

    def __init__(self, max_page: int):
        super().__init__(style=get_button_colour("grey"), label="Go To Page")
        self.max_page = max_page

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        modal = PageModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.page.value:
            return
        try:
            p = int(modal.page.value)
            current = p - 1
        except ValueError:
            return await interaction.followup.send(
                content=f"Invalid page provided. Must be a number between 1-{self.max_page + 1}.",
                ephemeral=True,
            )
        if current > self.max_page or current < 0:
            return await interaction.followup.send(
                content=f"Invalid page provided. Must be a number between 1-{self.max_page + 1}.",
                ephemeral=True,
            )
        self.view.current_page = current
        await self.view.update_page(interaction)


class SelectPageMenu(discord.ui.Select):
    view: "NoobPaginator"

    def __init__(self, placeholder: str, options: List[discord.SelectOption]):
        super().__init__(
            placeholder=placeholder, min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        self.view.current_page = int(self.values[0])
        await self.view.update_page(interaction)


class NoobPaginator(NoobView):
    def __init__(
        self,
        *,
        obj: Union[commands.Context, discord.Interaction[Red]],
        pages: List[Union[str, discord.Embed]],
        use_select_menu: bool = False,
        use_page_button: bool = True,
        access_denied_as_video: bool = True,
        is_ephemeral: bool = False,
        timeout: float = 180,
    ):
        super().__init__(
            obj=obj,
            timeout_message=None,
            remove_embed_on_timeout=False,
            access_denied_as_video=access_denied_as_video,
            is_ephemeral=is_ephemeral,
            timeout=timeout,
        )
        self.pages = self.initialize_pages(pages)
        self.current_page = 0
        self.pages_length = len(pages)
        self.use_select_menu = use_select_menu
        self.use_page_button = use_page_button

    def initialize_pages(
        self, lst: List[Union[str, discord.Embed]]
    ) -> Dict[str, Union[str, discord.Embed]]:
        pages = {}

        if not lst:
            raise ValueError("The pages list is empty.")

        for index, page in enumerate(lst):
            if not isinstance(page, (str, discord.Embed)):
                raise TypeError(f"{page!r} is not of type str or discord.Embed.")
            pages[str(index)] = page

        return pages

    def get_page_kwargs(self, page_number: int) -> Dict[str, Union[str, discord.Embed]]:
        content_or_embed = self.pages[str(page_number)]

        kwargs = {"content": None, "embeds": [], "view": self}

        if isinstance(content_or_embed, str):
            kwargs["content"] = content_or_embed
        elif isinstance(content_or_embed, discord.Embed):
            kwargs["embeds"] = [content_or_embed]

        return kwargs

    def disable_items(self, index: int):
        maximum = self.pages_length - 1
        if index == 1:
            self.remove_item(self.first_page)
            self.remove_item(self.previous_page)
            self.remove_item(self.next_page)
            self.remove_item(self.last_page)
        elif index == 2:
            self.remove_item(self.first_page)
            self.remove_item(self.last_page)
            self.previous_page.disabled = self.current_page <= 0
            self.next_page.disabled = self.current_page >= maximum
        elif index >= 3:
            self.first_page.disabled = self.current_page <= 0
            self.previous_page.disabled = self.current_page <= 0
            self.next_page.disabled = self.current_page >= maximum
            self.last_page.disabled = self.current_page >= maximum

    async def start(self) -> None:
        self.disable_items(len(self.pages))
        if len(self.pages) >= 3:
            if self.use_page_button:
                self.add_item(SelectPageButton(self.pages_length - 1))
            if self.use_select_menu:
                select_options = [
                    discord.SelectOption(label=f"Page {i + 1}", value=i)
                    for i in range(len(self.pages))
                ]
                self.add_item(
                    SelectPageMenu(
                        placeholder="Select Page", options=select_options[:25]
                    )
                )
        kwargs = self.get_page_kwargs(self.current_page)

        if self.context is not None:
            self.message = await self.context.send(**kwargs)
        elif self.interaction is not None:
            if self.interaction.response.is_done():
                self.message = await self.interaction.followup.send(
                    **kwargs, ephemeral=self.ephemeral
                )
            else:
                await self.interaction.response.send_message(
                    **kwargs, ephemeral=self.ephemeral
                )
                self.message = await self.interaction.original_response()
        else:
            raise NoContextOrInteractionFound(
                "Cannot start a paginator without a context or interaction."
            )

    async def update_page(self, interaction: discord.Interaction[Red]) -> None:
        kwargs = self.get_page_kwargs(self.current_page)
        self.disable_items(len(self.pages))
        if interaction.response.is_done():
            await interaction.edit_original_response(**kwargs)
        else:
            await interaction.response.edit_message(**kwargs)

    @discord.ui.button(emoji="⏪", style=get_button_colour("grey"))
    async def first_page(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ) -> None:
        self.current_page = 0
        await self.update_page(interaction)

    @discord.ui.button(emoji="◀️", style=get_button_colour("grey"))
    async def previous_page(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ) -> None:
        self.current_page -= 1
        await self.update_page(interaction)

    @discord.ui.button(emoji="✖️", style=get_button_colour("red"))
    async def stop_page(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        if self.ephemeral:
            for x in self.children:
                x.disabled = True
            await interaction.edit_original_response(view=self)
        else:
            await interaction.message.delete()
        self.stop()

    @discord.ui.button(emoji="▶️", style=get_button_colour("grey"))
    async def next_page(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ) -> None:
        self.current_page += 1
        await self.update_page(interaction)

    @discord.ui.button(emoji="⏩", style=get_button_colour("grey"))
    async def last_page(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ) -> None:
        self.current_page = self.pages_length - 1
        await self.update_page(interaction)


class NoobConfirmation(NoobView):
    def __init__(
        self,
        *,
        obj: Union[commands.Context, discord.Interaction[Red]],
        confirm_action: str,
        access_denied_as_video: bool = True,
        is_ephemeral: bool = False,
        timeout: float = 180,
    ):
        super().__init__(
            obj=obj,
            timeout_message="You took too long to respond.",
            remove_embed_on_timeout=True,
            access_denied_as_video=access_denied_as_video,
            is_ephemeral=is_ephemeral,
            timeout=timeout,
        )
        self.value = None
        self.confirm_action = confirm_action

    async def start(self, **kwargs) -> Any:
        kwargs["view"] = self
        kwargs.pop("ephemeral", None)

        if self.context:
            self.interaction = None
            self.message = await self.context.send(**kwargs)
        else:
            self.context = None
            if self.interaction.response.is_done():
                self.message = await self.interaction.followup.send(
                    ephemeral=self.ephemeral, **kwargs
                )
            else:
                await self.interaction.response.send_message(
                    ephemeral=self.ephemeral, **kwargs
                )
                self.message = await self.interaction.original_response()

    @discord.ui.button(label="Yes", emoji="✔️", style=get_button_colour("green"))
    async def yes_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button[Self]
    ):
        for x in self.children:
            x.disabled = True
        self.value = True
        self.stop()
        await interaction.response.edit_message(
            content=self.confirm_action, embed=None, view=self
        )

    @discord.ui.button(label="No", emoji="✖️", style=get_button_colour("red"))
    async def no_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button[Self]
    ):
        for x in self.children:
            x.disabled = True
        self.value = False
        self.stop()
        await interaction.response.edit_message(
            content="Alright not doing that then.", embed=None, view=self
        )

    async def on_timeout(self):
        self.value = False
        return await super().on_timeout()
