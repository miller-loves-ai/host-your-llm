import modal

############################## SETUP ###############################

app = modal.App("lumo-70b") #app name
API_KEY = "make-up-your-own-api-key"

# Set up the container image
vllm_image = (
    modal.Image.from_registry("vllm/vllm-openai:v0.6.6.post1", 
        setup_dockerfile_commands=["RUN ln -s /usr/bin/python3 /usr/bin/python"]
    )
    .entrypoint([])
)

# select GPU and amount
GPU = modal.gpu.H100(count=1)

# set up the volume and model path, must be the same as the one in the 
# download script
MODELS_VOLUME = "lumo70b"
MODELS_DIR = "/lumo70b"


# set up the command line for vllm
# you may need to adjust max_model_len to fit your GPU and your task
# also longer max model len results in longer warm-up time
COMMEND_LINE = f"vllm serve {MODELS_DIR}/lumolabs-ai/Lumo-70B-Instruct/Lumo-70B-Instruct-FT-Q4_0.gguf " + \
                f"--tokenizer {MODELS_DIR}/NaniDAO/Llama-3.3-70B-Instruct-ablated " + \
                f"--api-key {API_KEY} " + \
                "--max_model_len=16000 " + \
                "--seed 42 " + \
                "--dtype auto " + \
                "--gpu_memory_utilization 0.90 " + \
                "--served_model_name lumolabs-ai/Lumo-70B-Instruct " + \
                "--enforce-eager" # enable eager mode to speed up the warmup

# Seconds to keep the container alive after the last request
# Since warmup take a lot of time, you may want to set this larger than your 
# gap between consecutive API call.
CONTAINER_IDLE_TIMEOUT = 5 
# Most of the time is wasted in warming up so we would rather queue more 
# inputs into VLLM managed queue instead of setting up more containers
ALLOW_CONCURRENT_INPUTS = 10


############################## DEPLOY ###############################

# ## Load the model weights

try:
    volume = modal.Volume.lookup(MODELS_VOLUME, create_if_missing=False)
except modal.exception.NotFoundError:
    raise Exception("Download models first with modal run download_llama.py")

# ## Build a vLLM engine and serve it

MINUTES = 60  # seconds
HOURS = 60 * MINUTES

print("startup commend: ", COMMEND_LINE)

@app.function(
    image=vllm_image,
    gpu=GPU,
    container_idle_timeout=CONTAINER_IDLE_TIMEOUT,
    timeout=24 * HOURS,
    allow_concurrent_inputs=ALLOW_CONCURRENT_INPUTS, 
    volumes={MODELS_DIR: volume}
)
@modal.web_server(
    port=8000,
    startup_timeout=12*MINUTES
)
def serve():
    import subprocess
    subprocess.Popen(COMMEND_LINE, shell=True)