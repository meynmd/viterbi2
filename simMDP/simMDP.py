import sys
import random

class Simulator:
    def __init__(self):
        self.NumStates = 0
        self.NumActions = 0
        self.Transition = []
        self.Reward = []
        self.InitialState = 0
        self.TerminalStates = []
        self.StateDescriptions = []
        self.ActionDescriptions = []
        self.CurrentState = None
        self.StateActionHistory = []
        self.AccumReward = 0.



    '''
    reset the simulation
    '''
    def Start(self, state = None):
        if state == None:
            state = self.InitialState
        self.CurrentState = state
        self.StateActionHistory = []
        self.StateActionHistory = []
        self.AccumReward = 0.



    '''
    get all available actions
    '''
    def GetActions(self):
        if self.CurrentState in self.TerminalStates:
            return []
        elif self.CurrentState % 3 == 1:
            return [2]
        elif self.CurrentState % 3 == 0:
            return [0, 1]
        else:
            return [i for i in range(self.NumActions)]



    def GetAccumReward(self):
        return self.AccumReward



    def GetStateReward(self, state):
        return self.Reward[state]



    def GetCurrentState(self):
        return self.CurrentState



    def GetNumStates(self):
        return self.NumStates



    def GetNumActions(self):
        return self.NumActions



    '''
    take an action

    returns the new state after taking the action
    '''
    def TakeAction(self, action):
        if self.CurrentState in self.TerminalStates:
            return None

        self.StateActionHistory.append((self.CurrentState, action))
        probs = self.Transition[action][self.CurrentState]
        s = random.choices([i for i in range(self.NumStates)], probs)
        s = s[0]
        self.CurrentState = s
        self.AccumReward += self.Reward[s]
        return s



    '''
    load MDP from file
    '''
    def Load(self, path):
        file = open(path, 'r')
        if not file:
            raise(OSError)

        # read header data
        line = file.readline().split()
        headerData = [int(x) for x in line]
        self.NumStates = headerData[0]
        self.NumActions = headerData[1]
    
        # initialize self with appropriate number of states and actions
        self.Reward = [0. for i in range(self.NumStates)] 
        self.Transition = [[[0. for k in range(self.NumStates)] \
            for j in range(self.NumStates)] \
            for i in range(self.NumActions)]

        # read transition data
        for i in range(self.NumActions):
            file.readline()
            for j in range(self.NumStates):
                self.Transition[i][j] = [float(x) for x in file.readline().split()]

        # read reward data
        file.readline()
        rewardData = file.readline()
        rewardData = rewardData.strip('\t')
        self.Reward = [float(x) for x in rewardData.split()]

        # read initial, final states
        file.readline()
        self.InitialState = int(file.readline().strip('\t'))
        file.readline()
        line = file.readline()
        while line != '\n':
            self.TerminalStates.append(int(line.strip('\n')))
            line = file.readline()



        # read state descriptions
        self.StateDescriptions = ['' for i in range(self.NumStates)]
        for i in range(self.NumStates):
            try:
                stateData = file.readline()
                stateData = stateData.strip('\n')
                stateData = stateData.split('\t')
                if int(stateData[0]) != i:
                    print('Error reading state description numbers', file = sys.stderr)
                else:
                    self.StateDescriptions[i] = str(stateData[1])
            except:
                print('Error reading state descriptions', file = sys.stderr)

        # read action descriptions
        file.readline()
        self.ActionDescriptions = ['' for i in range(self.NumActions)]
        for i in range(self.NumActions):
            actionData = file.readline()
            actionData = actionData.strip('\n')
            actionData = actionData.split()
            if int(actionData[0]) != i:
                print('Error reading state description numbers', file = sys.stderr)
            else:
                self.ActionDescriptions[i] = str(actionData[1])



    '''
    get T(state, action, nextState)
    '''
    def GetTransProb(self, state, action, nextState):
        if action < self.NumActions and state < self.NumStates and nextState < self.NumStates:
            return self.Transition[action][state][nextState]
        else:
            print('array bounds error', file = sys.stderr)



    '''
    get string desciption of state
    '''
    def GetStateDesc(self, statenum):
        if statenum < self.NumStates:
            return self.StateDescriptions[statenum]



    def GetActionDesc(self, actnum):
        t = type(actnum)
        if t != type(1):
            return 'None'
        if actnum < self.NumActions:
            return self.ActionDescriptions[actnum]