from os import system

for i in range(3):
    system("python3 test.py")
    system("python3 rouge.py")
    system("mv scores.txt scores{}.txt".format(i))
    system("mv log.txt log{}.txt".format(i))
    system("mv scores{}.txt attempt3/".format(i))
    system("mv log{}.txt attempt3/".format(i))