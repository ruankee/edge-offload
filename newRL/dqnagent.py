import numpy as np
import os
from keras import *
from keras.layers import Dense
from keras.layers import Activation
from collections import deque
import random

from env import *
from constants import *
"""
   状态空间-本地执行时延,本地传输时延,边缘1执行时延,边缘2执行时延
   动作空间-0,1,2
   奖励-系统总时延与总能耗平衡值
"""

class DqnAgent:
    def __init__(self,pModel,tModel):
        self.expMemory=deque(maxlen=MEMORY_SIZE)
        self.endState=deque()
        if os.path.exists(pModel) and os.path.exists(tModel):
            self.predictModel=models.load_model(pModel)
            self.targetModel=models.load_model(tModel)
        else:
            self.predictModel=self.buildModel()
            self.targetModel=self.buildModel()
            self.targetModel.set_weights(self.predictModel.get_weights())
        self.updateTargetCount=0

    def addMemory(self, newMemory):
        self.expMemory.append(newMemory)

    def getQs(self, chooseModel, states):
        if len(states.shape)==1:
            states=states.reshape(int(len(states)/STATE_SIZE[0]),STATE_SIZE[0])
        if chooseModel=='p':
            return self.predictModel.predict(states)
        else:
            return self.targetModel.predict(states)

    def trainModel(self,episodeDone):
        trainX=[]
        trainY=[]
        if len(self.expMemory)<MEMORY_SIZE:
            return
        # 抽取经验，获得q估计与q目标值
        memoryBatch=np.array(random.sample(self.expMemory, BATCH_SIZE))
        currentStates=np.array([state[0] for state in memoryBatch])
        nextStates=np.array([state[2] for state in memoryBatch])
        currentQsList=self.getQs('p', currentStates)
        nextQsList=self.getQs('t', nextStates)
        # 根据q估计与q现实训练预测网络
        for i,(currentState,action,nextState,reward) in enumerate(memoryBatch):
            currentQs=currentQsList[i]
            targetQ=np.max(nextQsList[i])
            try:
                if self.endState.index(nextState)>-1:
                    currentQs[action]=reward
            except ValueError:
                currentQs[action]=reward+DISCOUNT_RATE*targetQ
            trainX.append(currentState)
            trainY.append(currentQs)
        self.predictModel.fit(np.array(trainX), np.array(trainY), batch_size=BATCH_SIZE, verbose=0)
        # 到达次数更新目标网络
        if episodeDone:
            self.updateTargetCount+=1
        if self.updateTargetCount>=UPDATE_TARGET_FLAG:
            self.targetModel.set_weights(self.predictModel.get_weights())
            self.updateTargetCount=0

    def getReward(self,task,env):
        if task.offloadAction==0 or task.dataSize==0:
            return 0
        mobile=env.mobiles[int(task.nodeFrom[-1])]
        mec=env.mecs[task.offloadAction-1]
        #
        localDelay = getProcessDelay(task,mobile.cpuCapacity)+getQueueWaitDelay(env.currentTime,mobile.processQueue)
        localEnergy = mobile.processPower*getProcessDelay(task,mobile.cpuCapacity)
        edgeDelay = getTransmitDelay(task,env.getTransmitSpeed())+getQueueWaitDelay(env.currentTime,mobile.transmitQueue)\
                   +getProcessDelay(task,mec.cpuCapacity)+getQueueWaitDelay(env.currentTime,mec.processQueue)
        edgeEnergy = mec.processPower*getProcessDelay(task,mec.cpuCapacity)+mobile.transmitPower*getTransmitDelay(task,env.getTransmitSpeed())
        #
        localConsumption = W1*localDelay+ (1-W1)*localEnergy
        edgeConsumption = W1*edgeDelay+ (1-W1)*edgeEnergy
        #print('l-delay:',localDelay,'l-energy:',localEnergy)
        #print('e-delay:',edgeDelay,'e-energy:',edgeEnergy)
        return localConsumption-edgeConsumption

    def buildModel(self):
        model=models.Sequential()
        model.add(Dense(32, input_shape=STATE_SIZE))
        model.add(Activation('relu'))
        model.add(Dense(64))
        model.add(Activation('relu'))
        model.add(Dense(64))
        model.add(Activation('relu'))
        model.add(Dense(ACTION_SIZE))
        model.add(Activation('linear'))
        model.compile(loss='mse', optimizer="adam", metrics=['accuracy'])
        return model

    def saveModel(self):
        self.predictModel.save(MODEL_NAME2)

def train():
    global EPSILON
    dqnAgent=DqnAgent(MODEL_NAME1,MODEL_NAME1)
    env=Env()
    for episode in range(EPISODES):
        env.reset()
        previousOperation=list()
        # 训练至模拟结束
        while not env.end():
            tasks=env.createTasks()
            for i in range(len(tasks)):
                task=tasks[i]
                if task.dataSize>0:
                    currentState=[task.dataSize,task.resourceReq['cpuReq'],env.getTransmitSpeed(),env.getMECLoad()[0],env.getMECLoad()[1]]
                    # 根据e-greedy作出动作
                    if np.random.rand()>EPSILON:
                        action=np.argmax(dqnAgent.getQs('p',np.array(currentState))[0])
                    else:
                        action=np.random.randint(0,ACTION_SIZE)
                    task.setOffloadAction(action)
                    reward=dqnAgent.getReward(task, env)
                    # 将(s,a,s',r)传入经验池
                    if env.timeSlots-env.interval<env.currentTime<env.timeSlots+env.interval:
                        dqnAgent.endState.append(currentState)
                    if len(previousOperation)==len(tasks):
                        newMemory=[previousOperation[i][0],previousOperation[i][1],currentState,previousOperation[i][2]]
                        dqnAgent.addMemory(newMemory)
                        previousOperation[i]=[currentState, action, reward]
                    else:
                        previousOperation.append([currentState,action,reward])
            env.step(tasks)
            env.currentTime+=env.interval
            # 训练网络
            dqnAgent.trainModel(env.end())
        print('EPSIDOE='+str(episode+1)+' done')
        # epsilon衰减
        if EPSILON>MIN_EPSILON:
            EPSILON-=EPSILON*0.01
            EPSILON=max(EPSILON, MIN_EPSILON)
    dqnAgent.saveModel()

def test():
    env=Env()
    dqn=DqnAgent(MODEL_NAME1,MODEL_NAME1)
    for i in range(1):
        alltasks=env.createAllTasks()
        #
        R = 0
        env.reset()
        for tasks in alltasks:
            for task in tasks:
                task.processedTime = 0
                task.processDelay = 0
                task.transmittedTime = 0
                task.transmitDelay = 0
                task.offloadAction = 0
        for tasks in alltasks:
            for i in range(len(tasks)):
                if tasks[i].dataSize>0:
                    tasks[i].offloadAction = random.randint(1, 2)
                    R += dqn.getReward(tasks[i], env)
                    # print(str(alltasks.index(tasks))+'-' + str(i) + ':',tasks[i].offloadAction,dqn.getReward(tasks[i], env))
                    # print('------------')
            env.step(tasks)
            env.currentTime += env.interval
        print('edge-R=', R)
        print('==========================')
        #
        R=0
        env.reset()
        for tasks in alltasks:
            for task in tasks:
                task.processedTime=0
                task.processDelay=0
                task.transmittedTime=0
                task.transmitDelay=0
                task.offloadAction=0
        for tasks in alltasks:
            for i in range(len(tasks)):
                if tasks[i].dataSize>0:
                    if random.uniform(0,1)>0.5:
                        tasks[i].offloadAction=random.randint(1,2)
                    R+=dqn.getReward(tasks[i],env)
                    #print(str(alltasks.index(tasks))+'-' + str(i) + ':', tasks[i].offloadAction,dqn.getReward(tasks[i], env))
                    #print('------------')
            env.step(tasks)
            env.currentTime+=env.interval
        print('half-R=',R)
        print('==========================')
        #
        env.reset()
        R=0
        for tasks in alltasks:
            for task in tasks:
                task.processedTime = 0
                task.processDelay = 0
                task.transmittedTime = 0
                task.transmitDelay = 0
                task.offloadAction=0
        for tasks in alltasks:
            for i in range(len(tasks)):
                if tasks[i].dataSize>0:
                    currentState = [tasks[i].dataSize, tasks[i].resourceReq['cpuReq'], env.getTransmitSpeed(), env.getMECLoad()[0],
                                    env.getMECLoad()[1]]
                    x = dqn.getQs('p', np.array(currentState))[0]
                    tasks[i].offloadAction = np.argmax(x)
                    R += dqn.getReward(tasks[i], env)
                    # print(str(alltasks.index(tasks))+'-'+str(i)+':',tasks[i].offloadAction,dqn.getReward(tasks[i],env))
                    # print('------------')
            env.step(tasks)
            env.currentTime+=env.interval
        print('dqn1-R=',R)
        print('=================================')

if __name__ == '__main__':
    test()

