import modal

""" Edit this file to download other models """

MODELS_VOLUME = "lumo8b"
MODELS_DIR = "/lumo8b"
DEFAULT_NAME = "lumolabs-ai/Lumo-8B-Instruct"
DEFAULT_REVISION = "001a641c32275f87a438a9a6c5088d4464b36491"
volume = modal.Volume.from_name(MODELS_VOLUME, create_if_missing=True)
ignore_patterns=[
    "*.pt",
    "*.bin",
    "*.pth",
    "*.safetensors",
    "*.json",
    "original/*",
] # Keep gguf
NEED_HF_TOKEN = False
EXTERNAL_TOKENIZER = "NaniDAO/Meta-Llama-3.1-8B-Instruct-ablated-v1"
TOKENIZER_REVISION = "4f3e53cbb106f493459690a84b87c83d646c8223"


""" You typically don't change the following code """

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        [
            "huggingface_hub",  # download models from the Hugging Face Hub
            "hf-transfer",  # download models faster with Rust
        ]
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)


MINUTES = 60
HOURS = 60 * MINUTES


app = modal.App(
    image=image,
    secrets=[  # add a Hugging Face Secret if you need to download a gated model
        modal.Secret.from_name("huggingface-secret", required_keys=["HF_TOKEN"])
    ] if NEED_HF_TOKEN else [],
)


@app.function(volumes={MODELS_DIR: volume}, timeout=4 * HOURS)
def download_model(model_name, model_revision, force_download=False):
    from huggingface_hub import snapshot_download, hf_hub_download

    volume.reload()

    snapshot_download(
        model_name,
        local_dir=MODELS_DIR + "/" + model_name,
        ignore_patterns=ignore_patterns,
        revision=model_revision,
        force_download=force_download,
    )

    if EXTERNAL_TOKENIZER:
        # hf_hub_download(repo_id=EXTERNAL_TOKENIZER, filename="config.json", revision=TOKENIZER_REVISION)
        hf_hub_download(repo_id=EXTERNAL_TOKENIZER, local_dir=MODELS_DIR + "/" + EXTERNAL_TOKENIZER, filename="tokenizer.json", revision=TOKENIZER_REVISION)
        hf_hub_download(repo_id=EXTERNAL_TOKENIZER, local_dir=MODELS_DIR + "/" + EXTERNAL_TOKENIZER, filename="tokenizer_config.json", revision=TOKENIZER_REVISION)
    volume.commit()


@app.local_entrypoint()
def main(
    model_name: str = DEFAULT_NAME,
    model_revision: str = DEFAULT_REVISION,
    force_download: bool = False,
):
    download_model.remote(model_name, model_revision, force_download)


if __name__ == "__main__":
    main()
