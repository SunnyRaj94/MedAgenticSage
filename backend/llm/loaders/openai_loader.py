import openai


def load_model(model_name, config=None):
    """
    Load OpenAI API client.

    Args:
        model_name (str): OpenAI model name (e.g., gpt-3.5-turbo, gpt-4)
        config (dict): Contains API key and any other parameters.

    Returns:
        A function that wraps OpenAI API calls.
    """
    api_key = config.get("env", {}).get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required in config for OpenAI loader.")
    model_config = config.get("model_config", {}).get("openai", {}).get(model_name, {})
    model_id = model_config.get("model_identifier")

    openai.api_key = api_key

    def openai_chat(prompt, **kwargs):
        response = openai.ChatCompletion.create(
            model=model_id, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        return response.choices[0].message["content"]

    print(f"[OpenAI Loader] Ready to use model: {model_name}")
    return openai_chat
