from openai import OpenAI
import time

"""
your deployment log should look like this in the end.
  
✓ Created objects.
├── 🔨 Created mount xxxxxxx/app.py
└── 🔨 Created web function serve => https://xxxxx.modal.run. <--- this is the base_url
✓ App deployed in 120.761s! 🎉

Edit the base_url to the one you got from the deployment.
"""

client = OpenAI(
    api_key="make-up-your-own-api-key",
    base_url="https://xxxxx.modal.run/v1", # xxxxx is in the deployment log
)

# list all models
start_time = time.time()
models_response = client.models.list()
list_of_models = [model.id for model in models_response]
print("List of models:")
print(list_of_models)
model = list_of_models[0]
print(f"Time taken to warm up. {time.time() - start_time} seconds")

start_time = time.time()
completion = client.chat.completions.create(
    model=model,
    seed=42,
    temperature=0.9,
    top_p=0.5,
    max_tokens=512,
    n=1,
  messages=[ 
    {"role": "system", "content": "You are a helpful assistant that answer Solana related question."},
    {"role": "user", "content": "What is the role of SPL tokens?"}
  ]
)
print(f"Time taken to complete. {time.time() - start_time} seconds")
print("--------------------------------")
print(completion.choices[0].message.content)
