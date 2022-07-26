from console import Console
from entities import Entities
from map import Map
from textual.widgets import Placeholder
from websocket_app import WebsocketApp


class GameInterface(WebsocketApp):
    """Simple textual app.

    Just placeholders to be replaced once we get the client going.
    """

    async def on_mount(self) -> None:
        grid = await self.view.dock_grid(edge="left", name="left")

        grid.add_column(fraction=1, name="left")
        grid.add_column(fraction=2, name="center")
        grid.add_column(fraction=1, name="right")

        grid.add_row(fraction=1, name="top", min_size=2)
        grid.add_row(fraction=1, name="middle")
        grid.add_row(fraction=1, name="bottom")

        grid.add_areas(
            map_area="left-start|center-end,top-start|middle-end",
            entities_area="right,top-start|middle-end",
            events_area="left-start|center-end,bottom",
            available_commands_area="right,bottom",
        )

        self.console_widget = Console()
        # Testing websocket handling with websocket app.
        await self.websocket.send("Hello world!")

        grid.place(
            map_area=Map(),
            entities_area=Entities(),
            events_area=self.console_widget,
            available_commands_area=Placeholder(name="Available Commands"),
        )

    async def handle_messages(self):
        """Allows receiving messages from a websocket and handling them."""
        message = await self.websocket.recv()
        match message:
            case _:
                self.console_widget.out.add_log(message)


GameInterface.run(log="textual.log")