from __future__ import annotations

import contextlib
import discord

from redbot.core.bot import commands, Red
from redbot.core.utils import chat_formatting as cf

from typing import Dict, Optional, Union, List, Any, TYPE_CHECKING, Union

from .utility import get_button_colour, access_denied
from .exceptions import NoContextOrInteractionFound

if TYPE_CHECKING:
    from discord import Message, InteractionMessage, WebhookMessage

__all__ = ("NoobPaginator", "NoobConfirmation")


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
    def __init__(self, max_page: int):
        super().__init__(
            style=get_button_colour("grey"),
            label="Go To Page"
        )
        self.max_page = max_page

    async def callback(self, interaction: discord.Interaction[Red]) -> Any:
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
                ephemeral=True
            )
        if current > self.max_page:
            return await interaction.followup.send(
                content=f"Invalid page provided. Must be a number between 1-{self.max_page + 1}.",
                ephemeral=True
            )
        view: "NoobPaginator" = self.view
        view.current_page = current
        await view.update_page(interaction)

class SelectPageMenu(discord.ui.Select):
    def __init__(self, placeholder: str, options: List[discord.SelectOption]):
        super().__init__(
            placeholder=placeholder, min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction[Red]) -> Any:
        view: "NoobPaginator" = self.view
        view.current_page = int(self.values[0])
        await view.update_page(interaction)


class NoobPaginator(discord.ui.View):
    """
    originally from pranoy but i modified to work for red discord bot

    https://github.com/PranoyMajumdar/dispie/blob/main/dispie/paginator/__init__.py
    """

    message: Optional[Message] = None

    def __init__(
        self,
        pages: List[Any],
        *,
        timeout: Optional[float] = 180.0,
        delete_message_after: bool = False,
        use_select_menu: bool = False,
        use_page_button: bool = True,
        per_page: int = 1,
    ):
        super().__init__(timeout=timeout)
        self.delete_message_after: bool = delete_message_after
        self.current_page: int = 0
        self.ephemeral = False

        self.context: Optional[commands.Context] = None
        self.interaction: Optional[discord.Interaction[Red]] = None
        self.per_page: int = per_page
        self.pages: Any = pages
        total_pages, left_over = divmod(len(self.pages), self.per_page)
        if left_over:
            total_pages += 1

        self.max_pages: int = total_pages
        self.use_select_menu = use_select_menu
        self.use_page_button = use_page_button

    def stop(self) -> None:
        self.message = None
        self.context = None
        self.interaction = None

        super().stop()

    def get_page(self, page_number: int) -> Any:
        if page_number < 0 or page_number >= self.max_pages:
            self.current_page = 0
            return self.pages[self.current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        base = page_number * self.per_page
        return self.pages[base : base + self.per_page]

    def format_page(self, page: Any) -> Any:
        return page

    async def get_page_kwargs(self, page: Any) -> Dict[str, Any]:
        formatted_page = await discord.utils.maybe_coroutine(self.format_page, page)

        kwargs = {"content": None, "embeds": [], "view": self}
        if isinstance(formatted_page, str):
            kwargs["content"] = formatted_page
        elif isinstance(formatted_page, discord.Embed):
            kwargs["embeds"] = [formatted_page]
        elif isinstance(formatted_page, list):
            if not all(isinstance(embed, discord.Embed) for embed in formatted_page):
                raise TypeError("All elements in the list must be of type Embed")

            kwargs["embeds"] = formatted_page
        elif isinstance(formatted_page, dict):
            return formatted_page

        return kwargs

    async def update_page(self, interaction: discord.Interaction) -> None:
        if self.message is None:
            self.message = interaction.message

        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        self.disable_items(len(self.pages))
        if interaction.response.is_done():
            await self.message.edit(**kwargs)
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
        self.stop()
        if self.ephemeral:
            for x in self.children:
                x.disabled = True
            await interaction.response.edit_message(view=self)
        else:
            await interaction.message.delete()

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
        self.current_page = self.max_pages - 1
        await self.update_page(interaction)

    def disable_items(self, index: int):
        maximum = self.max_pages - 1
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

    async def start(
        self,
        obj: Union[commands.Context, discord.Interaction[Red]],
        ephemeral: bool = False,
    ) -> Optional[Union[Message, InteractionMessage, WebhookMessage]]:
        self.ephemeral = ephemeral
        if isinstance(obj, commands.Context):
            self.context = obj
            self.interaction = None
        else:
            self.context = None
            self.interaction = obj

        if self.message is not None and self.interaction is not None:
            await self.update_page(self.interaction)
        else:
            self.disable_items(len(self.pages))
            if len(self.pages) >= 3:
                if self.use_page_button:
                    self.add_item(SelectPageButton(self.max_pages - 1))
                if self.use_select_menu:
                    select_options = [
                        discord.SelectOption(label=f"Page {i + 1}", value=i)
                        for i in range(len(self.pages))
                    ]
                    self.add_item(
                        SelectPageMenu(placeholder="Select Page", options=select_options[:25])
                    )
            kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
            if self.context is not None:
                self.message = await self.context.send(**kwargs)
            elif self.interaction is not None:
                if self.interaction.response.is_done():
                    self.message = await self.interaction.followup.send(
                        **kwargs, ephemeral=ephemeral
                    )
                else:
                    await self.interaction.response.send_message(
                        **kwargs, ephemeral=ephemeral
                    )
                    self.message = await self.interaction.original_response()
            else:
                raise NoContextOrInteractionFound(
                    "Cannot start a paginator without a context or interaction."
                )

        return self.message

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if self.ephemeral and self.interaction:
            return True
        if not interaction.user:
            return True
        if await interaction.client.is_owner(interaction.user):
            return True
        if self.context and (self.context.author == interaction.user):
            return True
        if self.interaction and (self.interaction.user == interaction.user):
            return True
        await interaction.response.send_message(content=access_denied(), ephemeral=True)
        return False

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        with contextlib.suppress(
            Exception
        ):
            await self.message.edit(view=self)
        self.stop()


class NoobConfirmation(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.ephemeral = False
        self.confirm_action: str = None
        self.context: commands.Context = None
        self.interaction: discord.Interaction[Red] = None
        self.message: discord.Message = None
        self.value = None

    async def start(
        self,
        obj: Union[discord.Interaction, commands.Context],
        confirm_action,
        ephemeral=False,
        *args,
        **kwargs,
    ):
        if isinstance(obj, (commands.Context, discord.Interaction)):
            if isinstance(obj, commands.Context):
                self.context = obj
                self.interaction = None
                msg = await obj.send(view=self, *args, **kwargs)
            else:
                self.interaction = obj
                self.context = None
                if self.interaction.response.is_done():
                    msg = await self.interaction.followup.send(
                        view=self, ephemeral=ephemeral, *args, **kwargs
                    )
                else:
                    await self.interaction.response.send_message(
                        ephemeral=ephemeral, view=self, *args, **kwargs
                    )
                    msg = await self.interaction.original_response()
            self.message = msg
            self.ephemeral = ephemeral
            self.confirm_action = confirm_action
        else:
            raise NoContextOrInteractionFound("No Context or Interaction found.")

    @discord.ui.button(label="Yes", style=get_button_colour("green"))
    async def yes_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        for x in self.children:
            x.disabled = True
        self.value = True
        self.stop()
        await interaction.response.edit_message(
            content=self.confirm_action, embed=None, view=self
        )

    @discord.ui.button(label="No", style=get_button_colour("red"))
    async def no_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        for x in self.children:
            x.disabled = True
        self.value = False
        self.stop()
        await interaction.response.edit_message(
            content="Alright not doing that then.", embed=None, view=self
        )

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if self.ephemeral and self.interaction:
            return True
        if not interaction.user:
            return True
        if await interaction.client.is_owner(interaction.user):
            return True
        if self.context and (self.context.author == interaction.user):
            return True
        if self.interaction and (self.interaction.user == interaction.user):
            return True
        await interaction.response.send_message(content=access_denied(), ephemeral=True)
        return False

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        with contextlib.suppress(
            Exception
        ):
            await self.message.edit(
                content="You took too long to respond.", embed=None, view=self
            )
        self.stop()
