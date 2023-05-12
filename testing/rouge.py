from rouge_score import rouge_scorer
from sys import argv

scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

if len(argv) > 1:
    man = open(argv[1]).read().split("\n")
    bot = open(argv[2]).read().split("\n")
else:
    man = open("ref4.tsv").read().split("\n")
    bot = open("log.txt").read().split("\n")

scores = []

for i in range(120):
    man[i] = man[i].strip()
    bot[i] = bot[i].strip()
    if len(man[i]) and len(bot[i]):
        # print(man[i], bot[i])
        mname, mlocation, mtime, _, mparticipants = man[i].split(";")
        bname, blocation, btime, _, bparticipants = bot[i].split(";")
        score = []
        score.extend(list(*scorer.score(mname, bname).values()))
        score.extend(list(*scorer.score(mlocation, blocation).values()))
        score.extend(list(*scorer.score(mparticipants, bparticipants).values()))
        scores.append(score)
    elif man[i] == bot[i]:
        scores.append([1, 1, 1, 1, 1, 1, 1, 1, 1])
    else:
        scores.append([0, 0, 0, 0, 0, 0, 0, 0, 0])

avgs = []
for column in zip(*scores): 
    avgs.append(sum(column) / len(column))
scores.append(avgs)

open("scores.txt", "w").write("\n".join([",".join(map(str, s)) for s in scores]))
