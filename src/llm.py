"""
Centralized LLM access for the NPC evaluation framework.

Every model call goes through call_llm() here — the world/character generation
in WorldCreation.py (via API_helper) and the NPC / validator turns in
evaluation.py. Provider mechanics for ollama, huggingface, and gemini live in
this one module; each caller only picks a provider + model.

To generate worlds with a local HuggingFace model instead of ollama, change
the GENERATION MODEL block below:
    GEN_PROVIDER = "huggingface"
    GEN_MODEL    = "google/gemma-2-9b-it"   # any chat model with a chat template
"""

from ollama import Client


SUPPORTED_PROVIDERS = ["gemini", "huggingface", "ollama"]
HF_MAX_NEW_TOKENS = 2048


####################################  Gemini #################################### 

def _call_gemini(model, system_prompt, user_message, temperature) -> str:
    from google import genai  # lazy: only needed when the gemini provider is used
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                {"role": "user", "parts": [{"text": user_message}]}
            ],
            config={
                "system_instruction": system_prompt,
                "temperature": temperature,
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f"  [!] Gemini error: {e}")
        return "[ERROR]"

#################################### HuggingFace #################################### 
_HF_MODELS: dict = {}  # model_name -> (tokenizer, model), loaded on first use


def _get_hf_model(model_name: str):
    """Load (once) and cache a local HF causal-LM + tokenizer for model_name.
    """
    if model_name in _HF_MODELS:
        return _HF_MODELS[model_name]

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"[*] Loading HF model {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"[*] HF model loaded ({'cuda' if torch.cuda.is_available() else 'cpu'})")

    _HF_MODELS[model_name] = (tokenizer, model)
    return tokenizer, model


def _hf_chat_request(model, messages, temperature):
    """Generate one completion from a local HF chat model.
    """
    import torch

    tokenizer, hf_model = _get_hf_model(model)

    try:
        formatted = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )
    except Exception:
        # Some chat templates (e.g. Gemma) reject a system role; fold the
        # system turn into the first user turn and retry.
        merged, sys_text = [], ""
        for m in messages:
            if m["role"] == "system":
                sys_text = m["content"]
            elif m["role"] == "user" and sys_text:
                merged.append({"role": "user",
                               "content": f"{sys_text}\n\n{m['content']}"})
                sys_text = ""
            else:
                merged.append(m)
        formatted = tokenizer.apply_chat_template(
            merged, tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )

    inputs = tokenizer(
        formatted, return_tensors="pt", truncation=True, max_length=4096
    ).to(hf_model.device)

    gen_kwargs = {
        "max_new_tokens": HF_MAX_NEW_TOKENS,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if temperature and temperature > 0:
        gen_kwargs.update(do_sample=True, temperature=temperature, top_p=0.9)
    else:
        gen_kwargs.update(do_sample=False)

    with torch.no_grad():
        outputs = hf_model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            **gen_kwargs,
        )

    generated = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=False).strip()


def _call_huggingface(model, system_prompt, user_message, temperature):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})
    return _hf_chat_request(model, messages, temperature)

#################################### Cleaup #################################### 
def unload_models(*model_names) -> None:
    """Evict cached HuggingFace models and release their CUDA memory.
    """
    import gc

    names = list(model_names) or list(_HF_MODELS.keys())
    for name in names:
        pair = _HF_MODELS.pop(name, None)
        if pair is None:
            continue
        tokenizer, model = pair
        try:
            # Pull weights back to CPU so the GPU tensors are released even if
            # something else still references the module briefly.
            model.to("cpu")
        except Exception:
            # Models dispatched with accelerate hooks (device_map="auto") can
            # refuse .to(); dropping the reference below still frees them.
            pass
        del tokenizer, model, pair

    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except ImportError:
        pass


#################################### Ollama #################################### 

def _call_ollama(model, system_prompt, user_message, temperature):
    client = Client(host="http://localhost:11434")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})
    resp = client.chat(model=model, messages=messages,
                       options={"temperature": temperature})
    return resp["message"]["content"].strip()

#################################### Providers and LLM Call #################################### 

_PROVIDERS_SINGLE = {
    "gemini": _call_gemini,
    "huggingface": _call_huggingface,
    "ollama": _call_ollama,
}


def call_llm(provider: str, model: str, system_prompt: str,
             user_message: str, temperature: float = 0.0) -> str:
    """Dispatch one LLM turn to a provider.
    """
    try:
        fn = _PROVIDERS_SINGLE[provider]
    except KeyError:
        raise KeyError(f"Unknown provider {provider!r}; supported: {SUPPORTED_PROVIDERS}")
    return fn(model, system_prompt, user_message, temperature)



#################################### Helpers #################################### 

def _content_to_str(content) -> str:
    """Flatten a message's `content` (str, or a list of {text: ...} parts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                texts.append(str(part["text"]))
            else:
                texts.append(str(part))
        return "".join(texts)
    return str(content)


def API_helper(provider, model, model_temperature,  messages) -> str:
    """
    This is the interface WorldCreation.py already calls; its call sites are
    unchanged.
    """

    system_parts, user_parts = [], []
    for m in messages:
        text = _content_to_str(m.get("content", ""))
        if not text:
            continue
        if m.get("role") == "system":
            system_parts.append(text)
        else:
            user_parts.append(text)

    return call_llm(
        provider,
        model,
        "\n\n".join(system_parts),
        "\n\n".join(user_parts),
        model_temperature,
    )