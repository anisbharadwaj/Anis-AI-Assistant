from enum import Enum


class AssistantState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    ERROR = "error"
