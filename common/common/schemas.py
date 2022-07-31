from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

Type = TypeVar("Type", bound=str)


class MessageBase(BaseModel, Generic[Type]):
    """Base schema for a message"""

    type: Type


class ChatMessage(MessageBase[Literal["chat"]]):
    """Sent by the client (or server) when they wish to chat with the rest of the server."""

    player_name: str
    chat_message: str


class InitializePlayer(MessageBase[Literal["init"]]):
    """Sent by the client when they want to initialize a player"""

    username: str


class PlayerSchema(BaseModel):
    """Represents the JSON for a player"""

    uid: int
    name: str
    allowed_actions: set[str]


class RegistrationSuccessful(MessageBase[Literal["registration_successful"]]):
    """Sent by the server when the player successfully registers."""

    player: PlayerSchema


class ActionNoTargetRequest(MessageBase[Literal["action"]]):
    """Request sent by the client when they want to do an action without a target."""

    action: str
    player: int  # The player that's trying to perform the action.


class ActionWithTargetRequest(MessageBase[Literal["action"]]):
    """Request sent by the client when they want to do an action with a target."""

    action: str
    target: int
    player: int  # The player that's trying to perform the action.


class MovementRequest(MessageBase[Literal["move"]]):
    """Request sent by the client when they want to move."""

    direction: str
    player: int


class ActionResponse(MessageBase[Literal["action_response"]]):
    """Response to an action which the client sent."""

    response: str


class ActionUpdateMessage(MessageBase[Literal["update"]]):
    """Message sent by the server after a game ticks.

    It contains a message to be displayed about the result of the player's queued action.
    """

    message: str


class RoomChangeUpdate(MessageBase[Literal["room_change"]]):
    """Message sent by the server after an entity enters or leaves a room."""

    room_uid: int
    entity_uid: int
    entity_name: str
    enters: bool  # If False then it's leaving.


class RoomInformationMessage(MessageBase[Literal["room_info"]]):
    """Message sent to a player that's entering a new room."""

    entities: list[RoomChangeUpdate]


class DEATH(MessageBase[Literal["DEATH"]]):
    """Too bad! You died.

    Sent to the player when they get an ice cream :P
    """


CLIENT_REQUEST = (
    ChatMessage
    | InitializePlayer
    | ActionNoTargetRequest
    | ActionWithTargetRequest
    | MovementRequest
)
SERVER_RESPONSE = (
    RegistrationSuccessful
    | ActionResponse
    | ChatMessage
    | ActionUpdateMessage
    | RoomChangeUpdate
    | DEATH
)
MESSAGE = CLIENT_REQUEST | SERVER_RESPONSE
