from dotenv import load_dotenv
import openai
import os

load_dotenv()

openai.api_key = os.getenv('CHATGPT_API_KEY')


def chatgpt_response(prompt):
    # response = openai.Completion.create(
    response = openai.ChatCompletion.create(
        # model="text-davinci-003",
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]["text"]
    return prompt_response

def davinci(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]["text"]

    return prompt_response

def turbo(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {"role": "system", "content": "You are a secretary that finds events in a conversation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]['message']['content']

    return prompt_response

# text-ada-001      "Capable of very simple tasks, usually the fastest model in the GPT-3 series, and lowest cost."
# text-babbage-001  "Capable of straightforward tasks, very fast, and lower cost."
# text-curie-001    "Very capable, but faster and lower cost than Davinci."
# text-davinci-003  "Most capable GPT-3 model. Can do any task the other models can do, often with higher quality, longer output and better instruction-following. Also supports inserting completions within text."
