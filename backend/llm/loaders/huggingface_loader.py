from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel, pipeline
import os


def load_model(model_name, config=None):
    """
    Load a Hugging Face model (locally or from hub).

    Args:
        model_name (str): Model name as defined in YAML.
        config (dict): Config containing YAML data + optional API keys.

    Returns:
        Hugging Face pipeline object.
    """
    # Load model details from config
    model_config = (
        config.get("model_config", {}).get("huggingface", {}).get(model_name, {})
    )
    if not model_config:
        raise ValueError(
            f"No config found for model '{model_name}' under 'huggingface'."
        )

    model_id = model_config.get("model_identifier")
    task = model_config.get("task", "text-generation")
    local_path = model_config.get("local_path")

    use_local = model_config.get("available_locally", False) and os.path.exists(
        local_path
    )

    # Handle token for Hugging Face Hub (if needed)
    hf_token = config.get("env", {}).get("HUGGINGFACE_API_KEY", None)
    auth_args = {"use_auth_token": hf_token} if hf_token else {}

    # Load tokenizer and model
    if use_local:
        print(f"[Hugging Face Loader] Loading '{model_name}' locally from {local_path}")
        model_path = local_path
    else:
        print(f"[Hugging Face Loader] Downloading '{model_name}' from Hugging Face Hub")
        model_path = model_id

    # Load based on task
    if task == "text-generation":
        tokenizer = AutoTokenizer.from_pretrained(model_path, **auth_args)
        model = AutoModelForCausalLM.from_pretrained(model_path, **auth_args)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    elif task == "feature-extraction":
        tokenizer = AutoTokenizer.from_pretrained(model_path, **auth_args)
        model = AutoModel.from_pretrained(model_path, **auth_args)
        pipe = pipeline("feature-extraction", model=model, tokenizer=tokenizer)
    else:
        raise ValueError(f"Unsupported task: {task}")

    return pipe
