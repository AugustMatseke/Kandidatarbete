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
                "content": "You are a secretary that finds events in a conversation and adds them to a calendar. You must follow the following format: Event, Location, Time, Date, Participants. You must also not write anything other than the results found, and that you follow the date format DD/MM/YYYY and the time format HH:MM.",
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


asdf = 1
open("log.txt", "w").write("")
for text in open("dataset2.tsv").read().strip().splitlines():
    print(asdf)
    asdf += 1
    
    conversation, *stuff = text.split("\t")
    prompt = f"Check if the following conversation is about an event, meeting or gathering. Specifically, check if it contains an event that can be written in a calendar. If it does, answer yes, otherwise answer no. The conversation is as follows:\n"
    bot_response = None
    event = False
    while True:
        try:
            bot_response = turbo(prompt + "\n".join(conversation.split(";")))
            if "yes" in bot_response.lower():
                event = True
            break
        except:
            print(traceback.format_exc(), file=stderr)
            print(conversation, file=stderr)
            print("retrying...", file=stderr)
            sleep(1)

    if event:
        prompt = f"The following conversation is about an event. Find the event, location, time, date, and participants. Attempt to return the absolute dates and times instead of the relative time, the current time and date is {today}. Return N/A for any values that aren't found. Do not write anything other than the results found. The conversation is as follows:\n"
        bot_response = None
        while True:
            try:
                bot_response = turbo(prompt + "\n".join(conversation.split(";")))
                break
            except:
                print(traceback.format_exc(), file=stderr)
                print(conversation, file=stderr)
                print("retrying...", file=stderr)
                sleep(1)

        out = ""     
        try:
            result = eventHandler(bot_response)
            print(result)
            if len(result) == 1:
                print("saving as:", ";".join(result[0]))
                out = ";".join(result[0]) + "\n"
            else:
                out = "\n"
        except:
            print(traceback.format_exc())
            # print(conversation)
            out = "\n"
    else:
        print("no event found")
        out = "\n"
    open("log.txt", "a").write(out)
