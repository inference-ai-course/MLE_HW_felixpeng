import sys
import openai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)

def get_completion(prompt, model="gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

prompt = "What is the capital of France?"
response = get_completion(prompt)
print(response)


while True:
    prompt = input("You: ")
    if prompt.lower() in ["quit","bye","exit"]:
        break
    print(get_completion(prompt))