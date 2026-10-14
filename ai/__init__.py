# Provider selection utilities
from ai.local_provider import LocalProvider
from ai.online_provider import OnlineProvider
from ai.provider import MockProvider
import os


def get_provider():
    name = os.getenv("AI_PROVIDER", "none").lower()
    if name == "local":
        return LocalProvider()
    if name == "online":
        return OnlineProvider()
    return MockProvider()
