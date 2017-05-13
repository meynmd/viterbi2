import sys
from collections import defaultdict
import decode as d
import time

# Observations : list of string
# TransitionProb : defaultdict of defaultdict of defaultdict mapping y1->y2->y3->p(y1, y2, y3)
# EmissionProb : defaultdict of defaultdict mapping y->x->p(x|y)
def ViterbiPath(Observations, TransitionProb, EmissionProb, StartSymbol = '<s>', EndSymbol = '</s>', Order = 2):
    # insert the appropriate amount of padding
    Observations = Order * [StartSymbol] + Observations + ['</s>']

    # graph : list of defaultdict of defaultdict for each observed state x,'
    # each dictionary maps probability of reaching state i after seeing states u and v
    graph = [defaultdict(lambda : defaultdict(float)) for o in Observations]

    trace = defaultdict(dict)
    states = TransitionProb.keys() + ['</s>']

    # initialize the probability graph
    for s in states:
        for i in range(Order):
            graph[i][StartSymbol][StartSymbol] = 1.
        graph[Order][s][s] = EmissionProb[Observations[Order]][s] * TransitionProb[StartSymbol][StartSymbol][s]

    # compute the rest
    for i in range(Order, len(Observations)):
        print 'i=' + str(i)
        for u in states:
            for v in states:
                graph[i][u][v] = max([
                    graph[i - 1][t][u] * TransitionProb[t][u][v] * EmissionProb[v][Observations[i]]
                    for t in states
                ])


    return max([graph[i][u][v] for u in states for v in states])



if __name__ == '__main__':
    ##########################################################
    observations = ['P']
    file_name = 'epron.probs'
    file_name1 = 'epron-jpron.probs'

    epron_data = d.read_file(file_name)
    TransitionProb,unique_words = d.get_prob(epron_data,Matt=True)

    if unique_words[1]==[None]:
        u_prior = unique_words[0]

    data = d.read_file(file_name1)
    EmissionProb, unique_words = d.get_prob(data,Noise=True)

    EmissionProb['<s>']['<s>'] = 1.
    EmissionProb['</s>']['</s>'] = 1.

    u_i_noise,u_o_noise=unique_words[0], unique_words[1]
    ###############################################

    s1 = time.clock()
    m = ViterbiPath(observations,TransitionProb,EmissionProb)
    print 'Time for running the Algorithm:', time.clock()-s1
    print 'Result: ' + str(m)