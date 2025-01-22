# LLM Model Deployment Guide

This 10 minutes tutorial walks you through setting up and deploying the Lumo-8B/Lumo-70B model using [Modal.com](https://modal.com/) for free. After running this tutorial, you will get an OpenAI compatible API.

Please notice that Modal and other serverless platforms suffer from cold starting latency (~3 minutes for Lumo-70B). If you are trying to build a latency sensitive application, please consider using GPU rental services.

[Modal.com](https://modal.com/) is a cloud function platform that allows you to deploy AI models with minimal configuration. You can create your account with just a few clicks without any credit card information.

Modal grants $30 credit per month for free, which should be enough for running your own agent on Lumo-8B.

## Prerequisites

Before you begin, make sure you have:
- Python 3.8 or higher installed on your system
- A Modal.com account (sign up at https://modal.com)

## Setup Steps

### Install Modal CLI:
   ```bash
   pip install modal
   ```

### Configure Modal:
   ```bash
   python -m modal setup
   ```
   Follow the instructions to log in to your Modal account through your web browser.

### Clone this repository and navigate to the model directory:
   ```bash
   git clone https://github.com/miller-loves-ai/host-your-llm.git
   cd host-your-llm/modal.com/lumo_8b  # For Lumo-8B
   # or
   cd host-your-llm/modal.com/lumo_70b # For Lumo-70B
   ```

### Download the model weights:
   ```bash
   python -m modal run download.py
   ```
   This will download the model on the modal cloud storage, not on your own machine.

### Deploy the application:
   Open `app.py` and modify the following settings if needed:
   ```python
app = modal.App("lumo-8b") # app name
API_KEY = "make-up-your-own-api-key"
```

And then run this line to create the deployment:

   ```bash
   python -m modal deploy app.py
   ```
   After successful deployment, Modal will provide you with an endpoint URL. Your deployment log should look like this.
   ```
   ✓ Created objects.
   ├── 🔨 Created mount xxxxxxx/app.py
   └── 🔨 Created web function serve => https://xxxxx.modal.run. <--- this is the endpoint url
   ✓ App deployed in 120.804s! 🎉
   ```

### Test the deployment:
Edit the endpoint URL in `test.py` to the one you got from the last step.

```
base_url="https://xxxxx.modal.run/v1",
```
And then run:
   ```bash
   pip install openai
   python ../test.py
   ```
   This script runs a test completion with your deployed model to verify everything is working correctly. This should finishs within 3 minutes for Lumo-8B or 4 minutes for Lumo-70B. The actual inference runs in a few seconds, but the warm up (starting up the container and initializing the model) takes around 2~3 minutes.

## Monitoring & Costs

- Monitor your usage and costs through the Modal dashboard at https://modal.com/apps

## What to do next?

- Adjust parameters like `max_model_len` and `CONTAINER_IDLE_TIMEOUT` in `app.py` to optimize the warm up time and to fit your needs. `CONTAINER_IDLE_TIMEOUT` is the number of second that the container is kept alive after your last api call. If you intent to manually interact with the model and don't care about the credit much, you can set it to very high and manually close the deployment after usage (the monthly free credit supports you to use H100 to run Lumo-70B for around 6 hours or L4 to run Lumo-8B for around 37 hours). If you are using it in agent framework like Eliza, you can keep it at the round 10 so that the container is kept alive during consecutive Eliza activity.
- If you are an early-stage startup or academic, you may be eligible for up to $25K free credit. Details are here: https://modal.com/settings/plans

## Additional Resources

- [Modal Documentation](https://modal.com/docs)
