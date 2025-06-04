import yaml
import os
import re
import json
from pathlib import Path
from dotenv import dotenv_values

CONFIGS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = Path(CONFIGS_DIR).parent.resolve()

__include__ = [".env", "settings.yaml", "models.yaml"]

# Start with explicit path variables
replacements = {"<ROOT_PATH>": str(PROJECT_ROOT)}


def _load_yaml_file(filepath: str):
    """Loads a single YAML file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file '{filepath}': {e}")
            return {}
    return {}


def _load_json_file(filepath: str):
    """Loads a single YAML file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                globals()[sanitized_config_name] = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file '{filename}': {e}")
    return {}


def _load_env(filename: str = ".env"):
    """Loads environment variables from a .env file in the configs directory."""
    filepath = os.path.join(CONFIGS_DIR, filename)
    if os.path.exists(filepath):
        return dotenv_values(filepath)
    else:
        print(f"Warning: .env file '{filename}' not found at '{filepath}'")
        return {}


def _resolve_placeholders(data, original_data: dict):
    """
    Recursively replaces placeholder strings (e.g., '${key}' or '<KEY_NAME>')
    in a dictionary or list using values from the all_replacements dictionary.
    """
    if isinstance(data, dict):
        return {k: _resolve_placeholders(v, original_data) for k, v in data.items()}
    elif isinstance(data, list):
        return [_resolve_placeholders(item, original_data) for item in data]
    elif isinstance(data, str):
        for match in re.findall(r"\$\{(\w+)\}", data):
            replacement_value = original_data.get(match)
            data = data.replace(f"${{{match}}}", f"{replacement_value}")
        return data
    else:
        return data


def get_absolute_path(relative_path: str) -> str:
    """
    Returns the absolute path of a given relative path.
    Works on Linux, macOS, and Windows.
    """
    return os.path.abspath(os.path.expanduser(relative_path))


def go_up_directories(abs_path: str, levels: int = 1) -> str:
    """
    Go up 'levels' directories from the given absolute path.
    """
    path = Path(abs_path).resolve()
    for _ in range(levels):
        path = path.parent
    return str(path)


def recursive_replace(data, old_value, new_value):
    """
    Recursively replace string values in nested dictionaries/lists.
    """
    if isinstance(data, dict):
        return {
            key: recursive_replace(value, old_value, new_value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [recursive_replace(item, old_value, new_value) for item in data]
    elif isinstance(data, str):
        return data.replace(old_value, new_value)
    else:
        return data


def _sanitize_name(filename: str) -> str:
    """Sanitizes a filename to be a valid Python identifier."""
    # Replace hyphens with underscores
    name = filename.replace("-", "_")
    # Remove any character that isn't a letter, number, or underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    # Ensure it doesn't start with a number (though unlikely for config files)
    if name and name[0].isdigit():
        name = "_" + name
    return name


def load_file(filename):
    filepath = os.path.join(CONFIGS_DIR, filename)
    loaded_data = None
    # Get the name without extension
    config_name = os.path.splitext(filename)[0]
    # Sanitize name to be a valid Python identifier
    sanitized_config_name = _sanitize_name(config_name)
    if filename.endswith(".env"):
        loaded_data = _load_env(filepath)
        sanitized_config_name = (
            "env" if sanitized_config_name == "" else sanitized_config_name
        )
    # Load YAML files
    elif filename.endswith((".yaml", ".yml")):
        loaded_data = _load_yaml_file(filepath)
    # Load JSON files
    elif filename.endswith((".json")):
        loaded_data = _load_json_file(filepath)
    return loaded_data, sanitized_config_name


def print_directory_structure(
    startpath,
    indent_char="|   ",
    file_prefix="- ",
    include_extensions=[".py"],
    exclude_dirs=["__pycache__"],
):
    """
    Prints the directory structure in a tree-like format,
    with options for file extensions and directory exclusion.

    Args:
        startpath (str): The path to the directory to start traversing from.
        indent_char (str): The character(s) to use for indentation of subdirectories.
        file_prefix (str): The character(s) to use before file names.
        include_extensions (list, optional): List of file extensions (e.g., ['.py', '.txt'])
                                            to include. If None or empty, all files are included.
        exclude_dirs (list, optional): List of directory names (e.g., ['__pycache__', '.git'])
                                       to exclude from traversal and printing.
    """
    if not os.path.isdir(startpath):
        print(f"Error: '{startpath}' is not a valid directory.")
        return

    # Initialize defaults if None
    if include_extensions is None:
        include_extensions = []
    if exclude_dirs is None:
        exclude_dirs = []

    # Print the base name of the starting directory (the "root" of the tree)
    # It has no leading indent
    print(os.path.basename(startpath) + "/")

    # Iterate through the directory tree
    for root, dirs, files in os.walk(startpath):
        # Calculate the path relative to the startpath
        # Example: if startpath='/a/b', and root='/a/b/c/d', relative_path='c/d'
        relative_path = Path(root).relative_to(startpath)

        # Determine the level for indentation.
        # If relative_path is '.', it means 'root' is the same as 'startpath'.
        # In this case, its children (files/dirs directly in startpath) should be at level 1.
        # For deeper directories, the level is the number of path segments.
        level = len(relative_path.parts) if relative_path.parts != (".",) else 0

        # Indentation for the *current level's children*
        # So, level 0 (startpath's children) get 1 indent_char.
        # Level 1 (startpath's direct subdirectories' children) get 2 indent_chars.
        current_indent = indent_char * (
            level + 1
        )  # +1 to ensure first level has one indent

        # --- IMPORTANT: Prune directories for os.walk IN-PLACE ---
        # This prevents os.walk from entering excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # Print directories found at the current 'root' level
        # Sort for consistent output order
        for d in sorted(dirs):
            print(f"{current_indent}{d}/")

        # Print files found at the current 'root' level
        # Sort for consistent output order
        for f in sorted(files):
            # Apply file extension filter
            if not include_extensions or any(
                f.endswith(ext) for ext in include_extensions
            ):
                print(f"{current_indent}{file_prefix}{f}")


# Iterate through all files in the configs directory
for filename in os.listdir(CONFIGS_DIR):
    # print(filename)
    filepath = os.path.join(CONFIGS_DIR, filename)
    if filename not in __include__ or os.path.isdir(filepath):
        continue
    loaded_data, sanitized_config_name = load_file(filename)
    for key, value in replacements.items():
        loaded_data = recursive_replace(loaded_data, old_value=key, new_value=value)
    loaded_data = _resolve_placeholders(loaded_data, loaded_data)
    # print(sanitized_config_name)
    globals()[sanitized_config_name] = loaded_data
