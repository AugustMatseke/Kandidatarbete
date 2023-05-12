from os import system, path, listdir

n = 1
while path.exists("attempt{}".format(n)):
    if len(listdir("attempt{}".format(n))) == 0:
        break
    n += 1
else:
    system("mkdir attempt{}".format(n))

for i in range(3):
    system("py test.py")
    system("py rouge.py")
    system("mv scores.txt scores{}.txt".format(i))
    system("mv log.txt log{}.txt".format(i))
    system("mv scores{}.txt attempt{}/".format(i, n))
    system("mv log{}.txt attempt{}/".format(i, n))