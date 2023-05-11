from os import system

for i in range(3):
    system("py test.py")
    system("py rouge.py")
    system("mv scores.txt scores{}.txt".format(i))
    system("mv log.txt log{}.txt".format(i))