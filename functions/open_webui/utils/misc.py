"""
Mock utilities for OpenWebUI functions to support standalone testing.
"""


def pop_system_message(messages: list[dict]) -> tuple[dict | None, list[dict]]:
    """
    Extract and remove system message from messages list.

    Args:
        messages: List of message dictionaries.

    Returns:
        Tuple of (system_message or None, remaining_messages).
    """
    if not messages:
        return None, messages

    system_message = None
    remaining_messages = []

    for message in messages:
        if message.get("role") == "system":
            if system_message is None:
                system_message = message
        else:
            remaining_messages.append(message)

    return system_message, remaining_messages
