from langchain.chat_models import init_chat_model


def load_model(model_name, config=None):
    """
    Load a Groq model via LangChain's init_chat_model.

    Args:
        model_name (str): Model name (e.g., "llama3-8b-8192", "mixtral-8x7b").
                          This should be the Groq-specific model identifier.
        config (dict): Contains API key and other environment variables.

    Returns:
        A function that wraps Groq API calls.
    """
    if config is None:
        config = {}

    api_key = config.get("env", {}).get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is required in config for Groq loader.")
    model_config = config.get("model_config", {}).get("groq", {}).get(model_name, {})
    model_id = model_config.get("model_identifier")

    # Use init_chat_model to create the LLM instance
    # The 'model_provider="groq"' tells it to use ChatGroq under the hood.
    # Any kwargs passed here (like groq_api_key, temperature) are forwarded to ChatGroq.
    llm = init_chat_model(
        model_id,
        model_provider="groq",
        groq_api_key=api_key,
        temperature=0,  # You can customize this or other parameters as needed
    )

    def groq_chat(prompt, **kwargs):
        # LangChain's .invoke method is flexible; it can often take a string directly
        # and convert it to a HumanMessage.
        response = llm.invoke(prompt)
        return response.content

    print(f"[Groq Loader] Ready to use model: {model_name}")
    return groq_chat
