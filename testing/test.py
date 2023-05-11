from sys import stderr

from dotenv import load_dotenv
import openai
import os
import traceback

import datetime

from time import sleep


load_dotenv()

openai.api_key = os.getenv('CHATGPT_API_KEY')

# today = datetime.datetime.now().strftime('%H:%M %d/%m/%Y')
today = "12:00 18/04/2023"
print(today)

def davinci(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100,
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]["text"]

    return prompt_response


def turbo(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {
                "role": "system",
                "content": "You are a secretary that finds events in a conversation. Since you live in Sweden, the date format is DD/MM/YYYY and the time format is HH:MM.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,  # 0-2 lower= more deterministic, higher = more random
        max_tokens=100,
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]["message"]["content"]

    return prompt_response


def eventHandler(bot_response):
    response = bot_response.strip().splitlines()
    found = []
    print("kekw", response)
    event = response[0].strip()
    if event.startswith("Event"):
        event = event.split(":")[1].strip()
    if event == "N/A":
        return []

    location = response[1].strip()
    if location.startswith("Location"):
        location = location.split(":")[1].strip()

    time = response[2].strip()
    if time.startswith("Time"):
        time = time.split(":", maxsplit=1)[1].strip()
    # if time == "N/A":
    #     return []

    date = response[3].strip()
    if date.startswith("Date"):
        date = date.split(":")[1].strip()
    # if date == "N/A":
    #     return []

    time += " " + date

    participants = response[4].strip()
    if participants.startswith("Participants"):
        participants = participants.split(":")[1].strip()
    if " and " in participants:
        participants = participants.replace(" and ", ", ")
    if ", " in participants:
        participants = participants.split(", ")

    return [[event, location, time, participants[0], ", ".join(participants)]]



for text in open("dataset2.tsv").read().strip().splitlines():
    conversation, *stuff = text.split("\t")
    prompt = f"Observe the following conversation. If one single event is present, find the event, location, time, date, and participants. Return N/A for any that aren't found. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {datetime.datetime.now().strftime('%H:%M, %d %b %Y')}:\n"
    bot_response = None
    while True:
        try:
            bot_response = davinci(prompt + "\n".join(conversation.split(";")))
            break
        except:
            print(traceback.format_exc(), file=stderr)
            print(conversation, file=stderr)
            print("retrying...", file=stderr)
            sleep(1)

    out = ""     
    try:
        result = eventHandler(bot_response)
        print(len(result), result)
        if len(result) == 1:
            print("saving as:", ";".join(result[0]))
            out = ";".join(result[0]) + "\n"
        else:
            out = "\n"
    except:
        print(traceback.format_exc())
        # print(conversation)
        out = "\n"
    open("log.txt", "a").write(out)
