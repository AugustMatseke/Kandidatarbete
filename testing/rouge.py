from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

for case in range(3):
    man = open("ref2.tsv").read().split("\n")
    bot = open(f"attempt2/log{case}.txt").read().split("\n")

    scores = []

    for i in range(120):
        man[i] = man[i].strip()
        bot[i] = bot[i].strip()
        if len(man[i]) and len(bot[i]):
            # print(man[i], bot[i])
            try:
                mname, mlocation, mtime, _, mparticipants = man[i].split(";")
                bname, blocation, btime, _, bparticipants = bot[i].split(";")
            except:
                print(man[i])
                print(bot[i])

            score = []
            if mname == bname:
                score.extend([1, 1, 1])
            else:
                score.extend(list(*scorer.score(mname, bname).values()))
            
            if mlocation == blocation:
                score.extend([1, 1, 1])
            else:
                score.extend(list(*scorer.score(mlocation, blocation).values()))

            if mparticipants == bparticipants:
                score.extend([1, 1, 1])
            else:
                score.extend(list(*scorer.score(mparticipants, bparticipants).values()))
            
            scores.append(score)
        else:
            scores.append([0, 0, 0, 0, 0, 0, 0, 0, 0])

    avgs = []
    for column in zip(*scores): 
        avgs.append(sum(column) / len(column))
    scores.append(avgs)

    open(f"attempt3/scores{case}.txt", "w").write("\n".join([",".join(map(str, s)) for s in scores]))
