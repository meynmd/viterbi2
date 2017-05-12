import random
import sys
from collections import defaultdict

class MdpAgent:
    def ChooseAction(self, mdp):
        return None

    def TakeAction(self, mdp, action):
        return mdp.TakeAction(action)


    def TakeBestAction(self, mdp):
        action = self.ChooseAction(mdp)
        if action != None:
            return mdp.TakeAction(action)




class RandomAgent(MdpAgent):
    def __init__(self, parkProb):
        self.ParkProbability = parkProb


    def ChooseAction(self, mdp):
        actions = mdp.GetActions()
        if len(actions) == 0:
            #print('No actions to choose from', file = sys.stderr)
            return None
        else:
            r = random.random()
            if r > self.ParkProbability:
                return 1
            else:
                return 0




class ReflexAgent(MdpAgent):
    def __init__(self, parkProb):
        self.ParkProbability = parkProb


    def ChooseAction(self, simulator):
        actions = simulator.GetActions()
        if len(actions) == 0:
            #print('No actions to choose from', file = sys.stderr)
            return None
        else:
            stateDesc = simulator.GetStateDesc(simulator.GetCurrentState())
            tokens = stateDesc.replace(',', ' ')
            tokens = tokens.split()
            if tokens[1] == 'True':
                return 1
            else:
                r = random.random()
                if r > self.ParkProbability:
                    return 1
                else:
                    return 0                



class ConservativeReflexAgent(MdpAgent):
    def ChooseAction(self, simulator):
        actions = simulator.GetActions()
        if len(actions) == 0:
            return None
        else:
            stateDesc = simulator.GetStateDesc(simulator.GetCurrentState())
            tokens = stateDesc.replace(',', ' ')
            tokens = tokens.split()
            if tokens[1] == 'True':
                return 1
            else:
                data = tokens[0].strip()
                data = data.strip(']')
                space = data.split('[')
                num = int(space[1])
                if num < 7:
                    return 0
                else:
                    return 1




class PickyReflexAgent(MdpAgent):
    def ChooseAction(self, simulator):
        actions = simulator.GetActions()
        if len(actions) == 0:
            return None
        else:
            stateDesc = simulator.GetStateDesc(simulator.GetCurrentState())
            tokens = stateDesc.replace(',', ' ')
            tokens = tokens.split()
            if tokens[1] == 'True':
                return 1
            else:
                data = tokens[0].strip()
                data = data.strip(']')
                space = data.split('[')
                num = int(space[1])
                if num < 5:
                    r = random.random()
                    if r > float(num) / 5.:
                        return 1
                    else:
                        return 0  
                else:
                    return 1




class QLearningAgent(MdpAgent):
    def __init__(self, alpha, beta, epsilon):
        self.LearningRate = alpha
        self.DiscountFactor = beta
        self.GreedyProb = epsilon
        self.Reset()



    def Reset(self):
        self.QTable = {}
        self.History = {}
        self.LastSA = (None, None)
        self.Epoch = 0    



    def Start(self):
        self.LastSA = (None, None)
        self.Epoch += 1



    def SetEpsilon(self, epsilon):
        self.GreedyProb = epsilon



    def PrintTable(self, mdp):
        for ((state, action), q) in self.QTable.items():
            if state == None or action == None:
                continue
            print(mdp.GetStateDesc(state) + '\t'+ mdp.GetActionDesc(action) + '\t' + str(q))



    def MaxQ(self, mdpSim, state):
        qs = []

        for a in mdpSim.GetActions():
            q = self.QTable.get((state, a))
            if q == None:
                q = 0.
            qs.append(q)

        if len(qs) > 0:
            return max(qs)
        else:
            return 0.



    def ExploreExploit(self, mdpSim):
        state = mdpSim.GetCurrentState()
        actions = mdpSim.GetActions()
        numActions = len(actions)
        r = random.random()
        if r < self.GreedyProb:
            return random.choice(actions)
        else:
            qs = [self.QTable.get((state, action)) for action in actions]
            for i in range(len(qs)):
                if qs[i] == None:
                    qs[i] = 0.

            greedy = [actions[i] for i in range(numActions) if qs[i] == max(qs)]
            return random.choice(greedy)



    def ChooseAction(self, simulator):
        actions = simulator.GetActions()
        currentState = simulator.GetCurrentState()
        currentReward = simulator.GetStateReward(currentState)
        (prevState, prevAction) = self.LastSA

        #if len(actions) == 0:
        #    #if prevState != None and prevAction != None:
        #    #    self.QTable[self.LastSA] = simulator.GetStateReward(prevState)
        #    return None
    
        if prevState != None and prevAction != None:
            # how many times have we done prev action in prev state?
            n = self.History.get(self.LastSA)
            if n == None:
                n = 1
                self.History[self.LastSA] = n
            else:
                n += 1
                self.History[self.LastSA] = n

            # what is the current Q value for that state-action pair?
            q = self.QTable.get(self.LastSA)
            if q == None:
                q = 0.

            # Q-learning update
            
            r = simulator.GetStateReward(prevState)
            #print (r)
            Beta = self.DiscountFactor
            alpha = self.LearningRate
            mq = self.MaxQ(simulator, currentState)
            self.QTable[self.LastSA] = q + alpha * (r + Beta * mq - q)

        if len(actions) > 0:
            chosenAction = self.ExploreExploit(simulator)
            self.LastSA = (simulator.GetCurrentState(), chosenAction)
            return chosenAction
        else:
            return None
        
            






