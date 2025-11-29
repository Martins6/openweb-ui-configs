"""
summary: Generic CLI testing tool for OpenWebUI pipes/valves
input: Interactive prompts for function selection, valve configuration, and test messages
output: Streaming responses from the selected pipe with citations/sources
logic:
    1. Discover all Python files in functions/ directory
    2. Dynamically import and inspect for Pipe class with Valves
    3. Present interactive menu for function selection
    4. Dynamically read all valve configuration fields
    5. Prompt user to set each valve value with defaults shown
    6. If function has pipes() method, show available pipes/models
    7. Accept test message from user
    8. Call the pipe with streaming enabled
    9. Display response in real-time with citations
"""

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def discover_functions() -> list[dict[str, Any]]:
    """
    Discover all Python files in functions/ directory that contain a Pipe class.

    Returns:
        List of dicts with 'path', 'name', and 'module' keys.
    """
    functions_dir = Path(__file__).parent
    discovered = []

    for py_file in functions_dir.glob("*.py"):
        if py_file.name == "test_valve.py":
            continue

        try:
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[py_file.stem] = module
                spec.loader.exec_module(module)

                if hasattr(module, "Pipe"):
                    discovered.append(
                        {"path": str(py_file), "name": py_file.name, "module": module}
                    )
        except Exception as e:
            print(f"Warning: Could not load {py_file.name}: {e}")

    return discovered


def get_valve_fields(valves_class: type[BaseModel]) -> dict[str, Any]:
    """
    Extract all fields from a Pydantic Valves class with their metadata.

    Args:
        valves_class: The Valves BaseModel class.

    Returns:
        Dict mapping field name to field info dict.
    """
    fields = {}
    for field_name, field_info in valves_class.model_fields.items():
        fields[field_name] = {
            "default": field_info.default,
            "annotation": field_info.annotation,
            "description": field_info.description or "",
        }
    return fields


def prompt_for_value(field_name: str, field_info: dict[str, Any]) -> Any:
    """
    Prompt user for a field value with type conversion.

    Args:
        field_name: Name of the field.
        field_info: Field metadata dict.

    Returns:
        User-provided value converted to appropriate type.
    """
    default = field_info["default"]
    annotation = field_info["annotation"]
    description = field_info["description"]

    # Display prompt
    prompt = f"{field_name}"
    if description:
        print(f"  ({description})")
    if default is not None:
        prompt += f" [{default}]"
    prompt += ": "

    user_input = input(prompt).strip()

    # Use default if no input
    if not user_input and default is not None:
        return default

    # Type conversion
    if annotation == bool or (hasattr(annotation, "__origin__") and annotation.__origin__ == bool):
        return user_input.lower() in ("true", "t", "yes", "y", "1")
    elif annotation == int or (hasattr(annotation, "__origin__") and annotation.__origin__ == int):
        return int(user_input) if user_input else default
    elif annotation == float or (
        hasattr(annotation, "__origin__") and annotation.__origin__ == float
    ):
        return float(user_input) if user_input else default
    else:
        return user_input if user_input else default


def configure_valves(pipe_instance: Any) -> None:
    """
    Interactively configure valve settings for a pipe instance.

    Args:
        pipe_instance: Instance of the Pipe class.
    """
    if not hasattr(pipe_instance, "valves"):
        print("No valves to configure.")
        return

    valves_class = type(pipe_instance.valves)
    fields = get_valve_fields(valves_class)

    print("\nConfigure Valves:")
    print("-" * 50)

    for field_name, field_info in fields.items():
        value = prompt_for_value(field_name, field_info)
        setattr(pipe_instance.valves, field_name, value)

    print("-" * 50)


def select_pipe(pipe_instance: Any) -> str | None:
    """
    If the pipe has multiple models/pipes, let user select one.

    Args:
        pipe_instance: Instance of the Pipe class.

    Returns:
        Selected pipe ID or None if no pipes() method exists.
    """
    if not hasattr(pipe_instance, "pipes"):
        return None

    pipes = pipe_instance.pipes()
    if not pipes:
        return None

    print("\nAvailable pipes:")
    for i, pipe in enumerate(pipes, 1):
        print(f"{i}. {pipe['name']} (id: {pipe['id']})")

    while True:
        choice = input(f"\nSelect pipe [1-{len(pipes)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(pipes):
                return pipes[idx]["id"]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


async def mock_event_emitter(event: dict) -> None:
    """
    Mock event emitter for testing that displays sources/citations.

    Args:
        event: Event dict from the pipe.
    """
    if event.get("type") == "chat:completion":
        data = event.get("data", {})
        if "sources" in data:
            print("\n" + "=" * 50)
            print("SOURCES/CITATIONS:")
            print("=" * 50)
            for i, source in enumerate(data["sources"], 1):
                source_info = source.get("source", {})
                print(f"\n[{i}] {source_info.get('name', 'Source')}")
                urls = source_info.get("urls", [])
                for url in urls:
                    print(f"  → {url}")
            print("=" * 50 + "\n")


async def test_pipe(pipe_instance: Any, pipe_id: str | None, messages: list[dict[str, str]]) -> str:
    """
    Test the pipe with messages and display streaming response.

    Args:
        pipe_instance: Instance of the Pipe class.
        pipe_id: Selected pipe ID (if applicable).
        messages: List of message dicts with 'role' and 'content' keys.

    Returns:
        The complete assistant response.
    """
    # Construct request body
    model = pipe_id if pipe_id else "test-model"
    if hasattr(pipe_instance, "type") and pipe_instance.type == "manifold" and pipe_id:
        model = f"manifold.{pipe_id}"

    body = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    print("\n" + "=" * 50)
    print("RESPONSE:")
    print("=" * 50)

    response_content = ""

    try:
        async for chunk in pipe_instance.pipe(body, __event_emitter__=mock_event_emitter):
            if isinstance(chunk, str):
                # Handle streaming text chunks (SSE format)
                if chunk.startswith("data:"):
                    try:
                        json_start = chunk.find("{")
                        if json_start != -1:
                            data = json.loads(chunk[json_start:])
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    print(content, end="", flush=True)
                                    response_content += content
                    except json.JSONDecodeError:
                        pass
            elif isinstance(chunk, dict):
                # Handle dict responses (non-streaming or formatted)
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    message_obj = chunk["choices"][0].get("message", {})
                    content = message_obj.get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        response_content += content

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"\nError during pipe execution: {e}")
        response_content = f"Error: {e}"

    return response_content


async def main() -> None:
    """Main interactive testing flow."""
    print("=" * 50)
    print("OpenWebUI Pipe/Valve Testing Tool")
    print("=" * 50)

    # Discover functions
    functions = discover_functions()

    if not functions:
        print("\nNo functions found in functions/ directory.")
        print("Make sure your function files contain a 'Pipe' class.")
        return

    # Display available functions
    print("\nAvailable functions:")
    for i, func in enumerate(functions, 1):
        print(f"{i}. {func['name']}")

    # Select function
    while True:
        choice = input(f"\nSelect function [1-{len(functions)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(functions):
                selected = functions[idx]
                break
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

    # Instantiate pipe
    pipe_class = selected["module"].Pipe
    pipe_instance = pipe_class()

    print(f"\nSelected: {selected['name']}\n")

    # Configure valves
    configure_valves(pipe_instance)

    # Select pipe/model if available
    pipe_id = select_pipe(pipe_instance)

    # Initialize conversation history
    messages = []

    # Continuous conversation loop
    print("\n" + "=" * 50)
    print("Continuous conversation mode enabled.")
    print("Press Ctrl+C or enter 'quit'/'exit' to stop.")
    print("=" * 50)

    try:
        while True:
            # Get test message
            message = input("\nYou: ").strip()

            if not message or message.lower() in ("quit", "exit"):
                print("\nExiting conversation.")
                break

            # Add user message to history
            messages.append({"role": "user", "content": message})

            # Test the pipe and get response
            response = await test_pipe(pipe_instance, pipe_id, messages)

            # Add assistant response to history
            if response:
                messages.append({"role": "assistant", "content": response})

    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Exiting.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
