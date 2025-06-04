import importlib
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel  # For type hinting

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


def load_llm_langchain(
    source: str, model_name: str, config: dict = None
) -> BaseChatModel:
    """
    Load an LLM model via LangChain's init_chat_model, supporting multiple sources.

    Args:
        source (str): The model provider (e.g., "huggingface", "groq", "openai",
                      "anthropic", "ollama", "together").
        model_name (str): The specific model name/identifier for the chosen source
                          (e.g., "llama3-8b-8192" for Groq, "Meta-Llama-3-8B-Instruct" for HuggingFace).
                          This should be the key used in your models.yaml under the source.
        config (dict, optional): A dictionary containing loaded configuration,
                                 including 'model_config' and 'env' (for API keys).
                                 Defaults to None.

    Returns:
        BaseChatModel: An initialized LangChain BaseChatModel instance.

    Raises:
        ValueError: If configuration is missing or invalid.
        RuntimeError: If LLM initialization fails.
    """
    if config is None:
        config = {}

    # 1. Extract model-specific configuration from the overall config
    # This assumes config['model_config'] has a structure like:
    # {'groq': {'LLaMA-3': {...}}, 'huggingface': {'LLaMA-3': {...}}, ...}
    model_specific_config = (
        config.get("model_config", {}).get(source, {}).get(model_name, {})
    )

    if not model_specific_config:
        raise ValueError(
            f"Model configuration not found for source '{source}' and model '{model_name}'. "
            "Please check your models.yaml and ensure it's loaded correctly."
        )

    # Get the actual model identifier to pass to init_chat_model
    # This is the value that is specific to the API/HuggingFace/Ollama
    model_id = model_specific_config.get("model_identifier")
    if not model_id:
        raise ValueError(
            f"Missing 'model_identifier' for model '{model_name}' under source '{source}' "
            "in your configuration. This should be the actual model string for the provider."
        )

    # 2. Prepare kwargs for init_chat_model
    init_kwargs = {
        "model": model_id,
        "model_provider": source,
        "temperature": model_specific_config.get(
            "temperature", 0.0
        ),  # Default to 0.0 for deterministic tasks
        # Add other common parameters from model_specific_config if you define them
        # e.g., "max_tokens": model_specific_config.get("max_tokens"),
    }

    # 3. Handle API keys for remote providers
    api_key_env_var = model_specific_config.get("api_key_env_var")
    if api_key_env_var:
        api_key = config.get("env", {}).get(api_key_env_var)
        if not api_key:
            raise ValueError(
                f"API key environment variable '{api_key_env_var}' not found in 'env' config. "
                f"Required for source '{source}' model '{model_name}'. "
                "Please ensure it's set in your .env file."
            )

        # Map generic API key to provider-specific kwarg for init_chat_model
        # This is crucial because init_chat_model expects specific kwarg names (e.g., groq_api_key)
        if source == "groq":
            init_kwargs["groq_api_key"] = api_key
        elif source == "openai":
            init_kwargs["openai_api_key"] = api_key
        elif source == "anthropic":
            init_kwargs["anthropic_api_key"] = api_key
        elif source == "together":
            init_kwargs["together_api_key"] = api_key
        # Add other API providers as needed following their respective LangChain integration docs
        # If a provider is not explicitly mapped, init_chat_model might try to use a generic 'api_key'
        # or it might fail if the provider's integration expects a specific kwarg.
        else:
            print(
                f"Warning: API key for provider '{source}' is not explicitly mapped. "
                "Attempting to pass as generic 'api_key'. This might not work for all providers."
            )
            init_kwargs["api_key"] = api_key  # Fallback

    # 4. Handle specific parameters for local models (HuggingFace, Ollama)
    if source == "huggingface":
        # For HuggingFace, init_chat_model can take 'token' for gated models
        hf_token = config.get("env", {}).get("HF_TOKEN")
        if hf_token:
            init_kwargs["token"] = hf_token

        # If you want to specify a local cache directory for HuggingFace models
        # init_kwargs["cache_dir"] = model_specific_config.get("local_path")
        # Note: 'local_path' should be fully resolved by your configs/__init__.py

    elif source == "ollama":
        # Ollama can take a base_url if not running on default localhost:11434
        # You might add an 'ollama_base_url' to your models.yaml or settings.yaml
        ollama_base_url = model_specific_config.get("ollama_base_url")
        if ollama_base_url:
            init_kwargs["base_url"] = ollama_base_url

    # 5. Initialize the LLM
    try:
        llm = init_chat_model(**init_kwargs)
        print(
            f"[LLM Loader] Successfully initialized model '{model_id}' from '{source}'."
        )
        return llm
    except Exception as e:
        # Catch any exceptions during initialization and provide a more informative error
        raise RuntimeError(
            f"Failed to initialize LLM for source '{source}' model '{model_name}' "
            f"with model_id '{model_id}'. Error: {e}"
        ) from e
