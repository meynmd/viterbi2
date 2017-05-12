import sys
from collections import defaultdict


def ViterbiPath(Observations, TransitionProb, EmissionProb, StartSymbol = '<s>', EndSymbol = '</s>', Order = 2):
    # insert the appropriate amount of padding
    Observations = [Order * StartSymbol] + Observations
    graph = [defaultdict(lambda : defaultdict(float)) for o in Observations]
    trace = defaultdict(dict)
    states = TransitionProb.keys()

    # initialize the probability graph
    for s in states:
        for i in range(Order):
            graph[i][StartSymbol][StartSymbol] = 1.
        #graph[Order][s][s] = EmissionProb[Observations[Order]][s] * TransitionProb[StartSymbol][StartSymbol][s]

    # compute the rest
    for i in range(Order, len(Observations)):
        for u in states:
            for v in states:
                graph[i][u][v] = max(\
                    [graph[i - 1][t][u] * TransitionProb[t][u][v] * EmissionProb[v][Observations[i]]
                    for t in states])

    return max([graph[i][u][v] for u in states for v in states])



if __name__ == '__main__':
    #lexName = 'lexicon.wfst'
    #bigramName = 'bigram.wfsa'
    #if len(sys.argv) > 2:
    #    lexName = sys.argv[1]
    #    bigramName = sys.argv[2]
    e = defaultdict(lambda : defaultdict(float))
    t = defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    e['D']['the']=0.5
    e['D']['a']=0.5
    e['N']['horse']=1.
    t['D']['N']['D'] = 1.
    t['<s>']['<s>']['D'] = 1.
    t['<s>']['D']['N'] = 1.
    m = ViterbiPath(["the", "horse", "the"], t, e)
    print(m)