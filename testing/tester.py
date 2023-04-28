from os import system

for i in range(10):
    system("python3 test.py")
    system("python3 rouge.py")
    system("mv scores.txt scores{}.txt".format(i))
    system("mv log.txt log{}.txt".format(i))