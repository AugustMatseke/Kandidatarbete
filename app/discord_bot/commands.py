import app.db_interface.db as db
import app.gcal.gcal_api as gcal

# This is a set of the names of all events in the database.
# It contains a dictionary of all events, with each event
# being a dictionary of all participants and their event ids.
events = dict()


def getevents():
    return events


def getevent(name: str):
    if name not in events:
        return None

    return db.getevent(name)


def addevent(user_id: str, name: str, time: str, location: str, participants: list):
    global events
    if name in events:
        return False
    db.addevent(name, time, location, str(user_id), participants)
    events[name] = dict()
    for participant in filter(str.isnumeric, participants):
        # try:
        event = gcal.add_event(participant, name, time, location=location)
        events[name][participant] = event["id"]
        # except:pass
    return True


def removeevent(user_id: str, name: str):
    global events
    if name not in events:
        return False

    name, time, date, owner, participants = getevent(name)
    if owner != str(user_id):
        return False

    if not db.removeevent(name, str(user_id)):
        return False

    for participant in events[name]:
        gcal.remove_event(participant, events[name][participant])

    return True


def modifyevent(user_id: str, name: str, time: str, location: str):
    if name not in events:
        return False

    event = getevent(name)
    if event[3] != str(user_id):
        return False

    db.modifyevent(name, time, location, str(user_id))
    for participant in event[4]:
        gcal.modify_event(
            user_id, events[name][participant], name, time, location=location
        )

    return True


def joinevent(user_id: str, name: str):
    if name not in events:
        return False

    if user_id in events[name]:
        return False

    if db.joinevent(name, str(user_id)):
        name, time, location, owner, _ = getevent(name)
        result = gcal.add_event(user_id, name, time, location=location)
        events[name][user_id] = result["id"]
        return True


def leaveevent(user_id: str, name: str):
    if name not in events:
        return False

    if user_id not in events[name]:
        return False

    if db.leaveevent(name, str(user_id)) and gcal.remove_event(
        user_id, events[name][user_id]
    ):
        del events[name][user_id]
        return True
    return False
