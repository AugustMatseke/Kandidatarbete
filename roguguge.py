from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)

man = open("man.tsv").read().strip().splitlines()
bot = open("bot.tsv").read().strip().splitlines()

for i in range(len(man)):
    mname, mlocation, mtime, mparticipants = man[i].split(";")
    bname, blocation, btime, bparticipants = bot[i].split(";")
    print("name\t", scorer.score(mname, bname))
    print("location\t", scorer.score(mlocation, blocation))
    # print(scorer.score(mtime, btime))
    print("participants\t", scorer.score(mparticipants, bparticipants))
