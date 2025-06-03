import together


def load_model(model_name, config=None):
    """
    Load Together API client.

    Args:
        model_name (str): Together model name (e.g., togethercomputer/llama-2-70b-chat)
        config (dict): Contains API key and any other parameters.

    Returns:
        A function that wraps Together API calls.
    """
    api_key = config.get("env", {}).get("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY is required in config for Together loader.")
    model_config = (
        config.get("model_config", {}).get("together", {}).get(model_name, {})
    )
    model_id = model_config.get("model_identifier")

    together.api_key = api_key

    def together_generate(prompt, **kwargs):
        response = together.Complete.create(
            model=model_id, prompt=prompt, max_tokens=512, temperature=0.7, **kwargs
        )
        return response["output"]["choices"][0]["text"]

    print(f"[Together Loader] Ready to use model: {model_name}")
    return together_generate
