import app.db_interface.db as db
import app.gcal.gcal_api as gcal
import app.discord_bot.discord_api as discord_api

# This is a set of the names of all events in the database.
# It contains a dictionary of all events, with each event
# being a dictionary of all participants and their event ids.
events = set()


class Event:
    name = ""
    time = ""
    location = ""
    owner = ""
    participants = {}

    def __str__(self) -> str:
        return f"Event {self.name} at {self.time} in {self.location} by {self.owner} with {self.participants.keys()}"

    def __init__(
        self, name: str, time: str, owner: str, location="", participants=dict()
    ):
        self.name = name
        self.time = time
        self.location = location
        self.owner = owner
        if participants == "{, }":
            self.participants = {}
        elif isinstance(participants, str):
            self.participants = eval(participants)
        else:
            self.participants = participants

    def isowner(self, user_id: str):
        return self.owner == user_id

    def isparticipant(self, user_id: str):
        return user_id in self.participants


def init_events():
    global events
    events = set()
    for event in db.getevents():
        events.add(Event(event[0], event[1], event[3], event[2], event[4]))


def getevents():
    return events


def getevent(name: str, user_id: str):
    global events
    event = None
    for e in events:
        if e.name == name and e.owner == user_id:
            event = e
            break
    if event == None:
        return False

    return db.getevent(name, user_id)


async def addevent(
    name: str, location: str, time: str, user_id: str, participants: list
):
    event = Event(name, time, user_id, location)

    global events
    for e in events:
        if e.name == name and e.owner == user_id:
            return False

    for participant in filter(str.isnumeric, participants):
        if not participant == "223424602150273024":
            continue
        gcal_event = gcal.add_event(participant, name, time, location=location)
        if gcal_event:
            event.participants[participant] = gcal_event["id"]
        else:
            await (
                await (
                    await discord_api.client.fetch_user(int(participant))
                ).create_dm()
            ).send(
                "You are a participant in an event, but you have not logged in to Google Calendar. If you would like to log in to Google Calendar, please reply with `auth calendar`. To join the event once you have logged in, go to the server where the event was mentioned and type `/joinevent "
                + name
                + "`."
            )

    print(event.participants)
    events.add(event)
    db.addevent(name, time, location, str(user_id), str(event.participants))
    return True


def removeevent(user_id: str, name: str):
    global events
    event = None
    for e in events:
        if e.name == name and e.owner == user_id:
            event = e
            break
    if event == None:
        return False

    if not db.removeevent(name, str(user_id)):
        return False

    for user_id, event_id in event.participants:
        gcal.remove_event(user_id, event_id)

    events.remove(event)

    return True


def modifyevent(user_id: str, name: str, time="", location=""):
    global events
    event = None
    for e in events:
        if e.name == name and e.owner == user_id:
            event = e
            break
    if event == None:
        return False

    if time:
        event.time = time
    if location:
        event.location = location

    db.modifyevent(name, time, location, str(event.participants), str(user_id))
    for participant in event.participants.values():
        gcal.modify_event(participant, user_id, name, time, location=location)

    return True


def joinevent(user_id: str, name: str, owner: str):
    global events
    event = None
    for e in events:
        if e.name == name and e.owner == owner:
            event = e
            break
    if event == None:
        return False

    if user_id in event.participants:
        return False

    name, time, location, _, _ = getevent(name, owner)
    result = gcal.add_event(user_id, name, time, location=location)
    event.participants[user_id] = result["id"]
    db.modifyevent(name, time, location, str(event.participants), str(owner))
    return True


def leaveevent(user_id: str, name: str, owner: str):
    global events
    event = None
    for e in events:
        if e.name == name and e.owner == owner:
            event = e
            break
    if event == None:
        return False

    if str(user_id) not in event.participants.keys():
        return False

    if gcal.remove_event(user_id, event.participants[user_id]):
        del event.participants[user_id]
        db.modifyevent(name, event.time, event.location, str(event.participants), str(user_id))
        return True
    return False
