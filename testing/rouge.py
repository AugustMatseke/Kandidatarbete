from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

man = open("ref.tsv").read().split("\n")
bot = open("log2.txt").read().split("\n")

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
    else:
        scores.append([0, 0, 0, 0, 0, 0, 0, 0, 0])

avgs = []
for column in zip(*scores): 
    avgs.append(sum(column) / len(column))
scores.append(avgs)

open("scores2.txt", "w").write("\n".join([",".join(map(str, s)) for s in scores]))
