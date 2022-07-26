import asyncio
from typing import Type

import websockets
from rich.console import Console
from textual.app import App
from textual.driver import Driver


class WebsocketApp(App):
    """A textual app meant to allow sending and receiving websocket messages."""

    def __init__(
        self,
        screen: bool = True,
        driver_class: Type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
        websocket=None,
    ):
        self.websocket = websocket
        super().__init__(screen, driver_class, log, log_verbosity, title)

    async def handle_messages(self):
        """This method is meant to be overriden in order to handle receiving messages from a websocket."""
        await asyncio.Future()

    @classmethod
    def run(
        cls,
        console: Console = None,
        screen: bool = True,
        driver: Type[Driver] = None,
        **kwargs,
    ):
        """Run the app.

        Args:
            console (Console, optional): Console object. Defaults to None.
            screen (bool, optional): Enable application mode. Defaults to True.
            driver (Type[Driver], optional): Driver class or None for default. Defaults to None.
        """
        # TODO: Allow connecting to a specific websocket port.
        async def run_app() -> None:
            async with websockets.connect("ws://localhost:8765") as websocket:
                app = cls(
                    screen=screen, driver_class=driver, websocket=websocket, **kwargs
                )

                # Creating asyncio tasks allows our TUI and our message receiving to happen concurrently.
                app_task = asyncio.create_task(app.process_messages())
                message_handler_task = asyncio.create_task(app.handle_messages())
                await app_task
                await message_handler_task

        asyncio.run(run_app())