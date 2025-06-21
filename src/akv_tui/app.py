import typing
from logging import getLogger

import pyperclip
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)

from akv_tui import services

logger = getLogger()


class VaultTUIApp(App):
    """Textual application."""

    TITLE = "Azure Key Vault Explorer"
    BINDINGS: typing.ClassVar = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self) -> None:
        """Initialize application."""
        super().__init__()
        self.vault_service = services.VaultService()
        self.vaults = self.vault_service.get_vaults()
        self.current_items = []
        self.modes = [
            ("secrets", "secrets"),
            ("keys", "keys"),
            ("certificates", "certificates"),
        ]
        self.selected_mode = "secrets"
        self.selected_vault = None

    def compose(self) -> ComposeResult:
        """Creates TUI interface.

        Returns:
            ComposeResult: Composition result

        Yields:
            Iterator[ComposeResult]: Widget iterable
        """
        yield Header()
        yield Vertical(
            Label("🔐 Select Azure Key Vault:"),
            Horizontal(
                Select(
                    options=[(v, v) for v in self.vaults],
                    id="vault-select",
                    prompt="Select your Key Vault",
                ),
                Select(
                    options=self.modes,
                    id="mode-select",
                    prompt="Select mode",
                    value=self.selected_mode,
                ),
            ),
            Vertical(  # ← new container for input and list view
                Input(placeholder="Search secrets/keys...", id="search-input"),
                ListView(id="results"),
                id="search-results-block",
            ),
        )
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handles events when the user triggers a Select.

        Args:
            event (Select.Changed): Change event from Select
        """
        if event.select.id == "vault-select":
            self.selected_vault = event.value
        elif event.select.id == "mode-select":
            self.selected_mode = event.value

        if self.selected_vault:
            self.handle_vault_changed()
        else:
            logger.debug("No vault selected.")

    def handle_vault_changed(self) -> None:
        """Handles vault changes."""
        vault_url = self.vaults[self.selected_vault]
        self.current_items = self.vault_service.get_items(vault_url, self.selected_mode)
        self.refresh_list()

    def refresh_list(self, query: str = "") -> None:
        """Refreshs ListView based on query.

        Args:
            query (str, optional): User input query. Defaults to "".
        """
        list_view = self.query_one("#results", ListView)
        list_view.clear()
        for item in filter(lambda i: query.lower() in i.lower(), self.current_items):
            list_view.mount(ListItem(Static(item, name=item)))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Updates ListView when input changes.

        Args:
            event (Input.Changed): Change event from Input
        """
        self.refresh_list(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Copies the value from the ListView to the clipboard on selection.

        Args:
            event (ListView.Selected): Selection event from ListView
        """
        name = event.item.children[0].name
        vault_url = self.vaults[self.selected_vault]
        try:
            value = self.vault_service.get_value(vault_url, name, self.selected_mode)
            pyperclip.copy(value)
            self.sub_title = f"Copied {self.selected_mode} '{name}' to clipboard"
        except Exception:  # noqa: BLE001
            self.sub_title = f"Failed to retrieve {self.selected_mode} '{name}'"

    def on_key(self, event: events.Key) -> None:
        """Handles key navigation for search list.

        This allows the user to navigate in the search list with arrow keys.

        Args:
            event (events.Key): Key event from keyboard
        """
        focus = self.focused
        input_widget = self.query_one("#search-input", Input)
        list_widget = self.query_one("#results", ListView)

        if focus is input_widget and event.key in {"right", "down"}:
            self.set_focus(list_widget)
            event.stop()

        elif focus is list_widget and event.key == "left":
            self.set_focus(input_widget)
            event.stop()
        elif focus is list_widget and event.key == "up":
            if not list_widget.index or list_widget.index == 0:
                self.set_focus(input_widget)
                event.stop()


def main() -> None:
    """Entrypoint for akv-tui."""
    VaultTUIApp().run()
