import sys
import random
import math
import simMDP
import mdpAgent

def QLearn(agent, simulator, numTrials, printHistory, training, startEpsilon = None, endEpsilon = None, showPercent = False): 
    totalReward = 0.
    onePercent = math.floor(numTrials / 100)
    for i in range(numTrials):
        if printHistory:
            print('\nTrial #{0}'.format(i + 1), file = sys.stderr)

        if training:
            if startEpsilon != None:
                agent.SetEpsilon(startEpsilon - (float(i) / numTrials) * (startEpsilon - endEpsilon))

            if showPercent and i % (10 * onePercent) == 0:
                print('{0}%...'.format(i / onePercent), file = sys.stderr)

        startState = random.randint(0, simulator.GetNumStates() - 1)
        startState = 3 * int(math.floor(startState / 3))
        simulator.Start(startState)
        """
        else:
            simulator.Start()
        """

        agent.Start()

        curState = simulator.GetCurrentState()
        while curState != None:
            bestAction = agent.ChooseAction(simulator)

            if printHistory:
                print('Current State: {0}\tAction: {1}'.format(\
                    simulator.GetStateDesc(curState), simulator.GetActionDesc(bestAction)),\
                    file = sys.stderr)
            
            curState = agent.TakeAction(simulator, bestAction)

        reward = simulator.GetAccumReward()
        totalReward += reward

        if printHistory:
            print('\nReward: {0}\n'.format(reward), file = sys.stderr)

    '''
    print('\n-----------------------------\n\n{0} trials\nAverage Reward: {1}\n'.format(\
        numTrials, totalReward / numTrials), file = sys.stderr)
    print('-----------------------------\n', file = sys.stderr)
    '''

    return totalReward / numTrials



def testSimpleAgent(agent, simulator, numTrials, printHistory): 
    totalReward = 0.
    for i in range(numTrials):
        if printHistory:
            print('\nTrial #{0}'.format(i + 1), file = sys.stderr)

        simulator.Start()      

        curState = simulator.GetCurrentState()
        while curState != None:
            bestAction = agent.ChooseAction(simulator)

            if printHistory:
                print('Current State: {0}\tAction: {1}'.format(\
                    simulator.GetStateDesc(curState), simulator.GetActionDesc(bestAction)),\
                    file = sys.stderr)
            
            curState = agent.TakeAction(simulator, bestAction)

        reward = simulator.GetAccumReward()
        totalReward += reward

        if printHistory:
            print('\nReward: {0}\n'.format(reward), file = sys.stderr)

    '''
    print('\n-----------------------------\n\n{0} trials\nAverage Reward: {1}\n'.format(\
        numTrials, totalReward / numTrials), file = sys.stderr)
    print('-----------------------------\n', file = sys.stderr)
    '''

    return totalReward / numTrials



def testAgents():
    # basic parameters
    agentTest = 3
    numTrials = 1000
    numTraining = 1000
    numEpochs = 15
    infile = 'mdp-2.txt'
    beta = 0.95
    alpha = 0.1
    startEpsilon = 0.75
    endEpsilon = 0.001
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    if len(sys.argv) > 2:
        alpha = sys.argv[2]
    if len(sys.argv) > 3:
        beta = sys.argv[3]

    randomAgent = mdpAgent.RandomAgent(0.1)
    reflexAgent = mdpAgent.ReflexAgent(0.1)
    consReflexAgent = mdpAgent.ConservativeReflexAgent()
    pickyReflexAgent = mdpAgent.PickyReflexAgent()
    qAgent = mdpAgent.QLearningAgent(alpha, beta, startEpsilon)

    agents = [('Random Agent', randomAgent),\
        ('Reflex Agent', reflexAgent),\
        ('Cons. Reflex Agent', consReflexAgent),\
        ('Picky Reflex Agent', pickyReflexAgent)]
    
    sim = simMDP.Simulator()
    sim.Load(infile)

    if agentTest == 2:
        for (name, agent) in agents:
            avgReward = testSimpleAgent(agent, sim, numTrials, False)
            print('Agent: {0}\tAverage reward: {1}\n\n'.format(name, avgReward))

    elif agentTest == 3:
        for i in range(numEpochs):
            #print('Training {0}...'.format(i))

            avgReward = QLearn(qAgent, sim, numTraining, False, True, startEpsilon, endEpsilon)
            #print('Agent: Q-Learning\t\tAverage reward: {0}'.format(avgReward))

            #print('\nTraining {0} complete.\n'.format(i))

            qAgent.SetEpsilon(0.)
            avgReward = QLearn(qAgent, sim, numTrials, False, False)
            print('{0} training runs\t\tAgent: Q-Learning\tAverage reward: {1}\n'.format((i+1)*numTraining, avgReward))

        qAgent.SetEpsilon(0.)
        QLearn(qAgent, sim, numTrials, True, False)



if __name__ == '__main__':
    testAgents()




def interactiveTest():
    infile = 'mdp.txt'
    sim = simMDP.Simulator()
    sim.Load(infile)

    while True:
        sim.Start()
        curState = sim.GetCurrentState()
        while sim.GetActions() != []:                
            print('Current State: {0}'.format(sim.GetStateDesc(curState), file = sys.stderr))
            action = input('\tAction? ')
            curState = sim.TakeAction(int(action))

        reward = sim.GetAccumReward()
        print('Reward: {0}\n\n'.format(reward))
