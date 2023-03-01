import db

print(db.init_database())
print(db.addevent("test", "test", "test", "test"))
print(db.modifyevent("test", "test", "test", "test2"))
print(db.modifyevent("test", "test", "test", "test"))
print(db.joinevent("test", "test2"))
print(db.joinevent("test", "test"))
print(db.leaveevent("test", "test2"))
print(db.leaveevent("test", "test"))
print(db.removeevent("test", "test2"))
print(db.removeevent("test", "test"))
