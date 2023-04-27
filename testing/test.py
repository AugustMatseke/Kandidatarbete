from sys import stderr

from dotenv import load_dotenv
import openai
import os
import traceback

import datetime

load_dotenv()

openai.api_key = 'dont fucking leak the token again smartass'

# today = datetime.datetime.now().strftime('%H:%M %d/%m/%Y')
today = "12:00 18/04/2023"
print(today)

def chatgpt_response(prompt):
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
        names = response[3].strip().split(", ")

        # print(";".join([event, location, time, ",".join(names)]))
        found.append([event, location, time, ",".join(names)])

    return found

with open('log.txt', 'w') as f:
    for text in open("dataset2.tsv").read().strip().splitlines()[1:]:
        conversation, *stuff = text.split("\t")
        # print("\n".join(conversation.split(";")))
        bot_response = chatgpt_response(
                prompt=f"Find all the events, meetings and/or other gatherings in the following conversation. For each detected event, meeting or gathering, return a list with the name, location, time and date, and participants. Do not label the values, just list them with semicolons in between. Return N/A for values that cannot be identified. If the event name is N/A or no participants are found, skip the entire event. If a time cannot be found, return N/A as the time. Otherwise, calculate the absolute time and date of each event given that the current time and date is {today}. The conversation is as follows: " + "\n".join(conversation.split(";")))
        try:
            result = eventHandler(bot_response)
            print(result)
            if len(result) == 1:
                f.write(";".join(result[0]) + "\n")
            else:
                f.write("\n")
        except:
            print(traceback.format_exc())
            print(conversation)
            f.write("\n")
