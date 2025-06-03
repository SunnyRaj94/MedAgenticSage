import anthropic


def load_model(model_name, config=None):
    """
    Load Anthropic (Claude) model.

    Args:
        model_name (str): Model name (e.g., claude-3-opus-20240229).
        config (dict): Contains API key and other params.

    Returns:
        A function that wraps Anthropic API calls.
    """
    api_key = config.get("env", {}).get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is required in config for Anthropic loader."
        )
    model_config = (
        config.get("model_config", {}).get("anthropic", {}).get(model_name, {})
    )
    model_id = model_config.get("model_identifier")

    client = anthropic.Anthropic(api_key=api_key)

    def claude_chat(prompt, **kwargs):
        response = client.messages.create(
            model=model_id,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.content[0].text

    print(f"[Anthropic Loader] Ready to use model: {model_name}")
    return claude_chat
