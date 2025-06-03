import importlib

SUPPORTED_SOURCES = {
    "huggingface": "backend.llm.loaders.huggingface_loader",
    "ollama": "backend.llm.loaders.ollama_loader",
    "openai": "backend.llm.loaders.openai_loader",
    "together": "backend.llm.loaders.together_loader",
    "groq": "backend.llm.loaders.groq_loader",
    "anthropic": "backend.llm.loaders.anthropic_loader",
}


def load_model(model_name, source, extra_config=None):
    """
    Load a model from the specified source.

    Args:
        model_name (str): The model's name (e.g., llama3, BioGPT).
        source (str): The provider (e.g., ollama, huggingface, openai).
        extra_config (dict, optional): API keys, paths, etc.

    Returns:
        A function that takes a prompt and returns a response.
    """
    if source not in SUPPORTED_SOURCES:
        raise ValueError(
            f"Unsupported source: {source}. Supported sources: {list(SUPPORTED_SOURCES.keys())}"
        )

    module_path = SUPPORTED_SOURCES[source]
    module = importlib.import_module(module_path)

    loader_func = getattr(module, "load_model", None)
    if loader_func is None:
        raise ImportError(f"{module_path} does not define load_model function.")

    return loader_func(model_name, config=extra_config or {})


def get_llm(model_name, source, extra_config=None):
    if source not in SUPPORTED_SOURCES:
        raise ValueError(
            f"Unsupported source: {source}. Supported sources: {list(SUPPORTED_SOURCES.keys())}"
        )

    module_path = SUPPORTED_SOURCES[source]
    module = importlib.import_module(module_path)

    loader_func = getattr(module, "get_llm", None)
    if loader_func is None:
        raise ImportError(f"{module_path} does not define get_llm function.")

    return loader_func(model_name, config=extra_config or {})
