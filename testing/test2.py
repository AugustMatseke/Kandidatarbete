from sys import stderr

from dotenv import load_dotenv
import openai
import os
import traceback

import datetime

load_dotenv()

openai.api_key = os.getenv('CHATGPT_API_KEY')
print(openai.api_key)

today = datetime.datetime.now().strftime('%H:%M %d/%m/%Y')
# today = "12:00 18/04/2023"
print(today)

# prompt = f"Find all the events, meetings or other gatherings in the following conversation. Find their names, locations, times, dates and participants. For each detected event, meeting or gathering, return a list with the name, location, time and date, and participants in that specific order. Do not label the values, just list them with semicolons in between. Return N/A for values that cannot be identified. If the event name is N/A or no participants are found, skip the entire event. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {datetime.datetime.now().strftime('%H:%M, %d %b %Y')}:\n"
prompt = f"Observe the following conversation. If an event is present, find the event, location, time, date, and participants. Return N/A for any that aren't found. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {datetime.datetime.now().strftime('%H:%M, %d %b %Y')}:\n"


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
            {"role": "system", "content": "You are a secretary that finds events in a conversation. Since you live in Sweden, the date format is DD/MM/YYYY and the time format is HH:MM."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]['message']['content']

    return prompt_response

def eventHandler(bot_response):
    responses = bot_response.strip().splitlines()
    print("asdf", responses, file=stderr)
    response = list(filter(lambda l: "N/A" in l, responses))
    if len(response) == 0:
        return 

    found = []
    for response in responses:
        response = response.split(";")
        # print(response)
        event = response[0].strip()
        if event.startswith("Event"):
            event = event.split(":")[1].strip()
        if event == "N/A":
            continue
        location = response[1].strip()
        time = response[2].strip()
        if time == "N/A":
            continue
        names = response[3].strip().split(", ")

        # print(";".join([event, location, time, ",".join(names)]))
        found.append([event, location, time, ",".join(names)])

    return found

text = prompt + open(0).read().strip()
print(text)
print(eventHandler(turbo(prompt=text)))
