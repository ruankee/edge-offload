import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import models
from tensorflow.keras import losses,optimizers,metrics
from tensorflow.keras.layers import Dense, Activation, Flatten
from tensorflow.keras.optimizers import Adam
from collections import deque
import random

from env import Env
"""
   状态空间-本地执行时延,本地传输时延,边缘1执行时延,边缘2执行时延
   动作空间-0,1,2
   奖励-系统总时延与总能耗平衡值
"""
EPISODES=10
MEMORY_SIZE=100
BATCH_SIZE=100
DISCOUNT_RATE=0.5
UPDATE_TARGET_FLAG=10
MOBILE_NUM=10
# 状态空间
STATE_SIZE=(4,)
# 动作空间
ACTION_SIZE=3
MIN_EPSILON=0.1
EPSILON=0.8

class DqnAgent:
    def __init__(self):
        self.exp_memory=deque(maxlen=MEMORY_SIZE)
        self.predict_model=self.build_model()
        self.target_model=self.build_model()
        self.target_model.set_weights(self.predict_model.get_weights())
        self.update_target_count=0

    def add_memory(self,new_memory):
        self.exp_memory.append(new_memory)

    def get_qs(self, model_flag, states):
        if model_flag=='p':
            return self.predict_model.predict(states)[0]
        else:
            return self.target_model.predict(states)[0]

    def train(self,episode_done):
        trainX=[]
        trainY=[]
        if len(self.exp_memory)<MEMORY_SIZE:
            return
        # 抽取经验，获得q估计与q目标值
        memoryBatch=random.sample(self.exp_memory,BATCH_SIZE)
        current_states=np.array([state[0] for state in memoryBatch])
        next_states=np.array([state[2] for state in memoryBatch])
        current_Qs_list=self.get_qs('p', current_states)
        next_Qs_list=self.get_qs('t', next_states)
        # 根据q估计与q现实训练预测网络
        for i,(current_state,action,next_state,r) in enumerate(memoryBatch):
            current_Qs=current_Qs_list[i]
            target_Q=np.max(next_Qs_list[i])
            if next_state>0:
                current_Qs[action]=r+DISCOUNT_RATE*target_Q
            else:
                current_Qs[action]=r
            trainX.append(current_state)
            trainY.append(current_Qs)
        self.predict_model.fit(np.array(trainX), np.array(trainY), batch_size=BATCH_SIZE, verbose=0)
        # 到达次数更新目标网络
        if episode_done:
            self.update_target_count+=1
        if self.update_target_count>=UPDATE_TARGET_FLAG:
            self.target_model.set_weights(self.predict_model.get_weights())
            self.update_target_count=0

    def build_model(self):
        model=models.Sequential()
        model.add(Dense(16, input_shape=STATE_SIZE))
        model.add(Activation('relu'))
        model.add(Dense(16))
        model.add(Activation('relu'))
        model.add(Dense(16))
        model.add(Activation('relu'))
        model.add(Dense(ACTION_SIZE))
        model.add(Activation('linear'))
        model.compile(loss='mse', optimizer=Adam, metrics=['accuracy'])

        return model

if __name__ == '__main__':
    for episode in range(EPISODES):
        env=Env()
        dqnAgent=DqnAgent()
        current_states=[[0,0,0,0] for i in range(MOBILE_NUM)]
        next_states=list()
        episode_done=False
        env.reset()
        # 训练至模拟结束
        R = 0
        while env.end()==False:
            tasks=env.create_tasks()
            actions=list()
            for i in range(len(tasks)):
                task=tasks[i]
                # 作出动作
                if np.random.rand()>EPSILON:
                    action=np.argmax(dqnAgent.get_qs('p',current_states[i]))
                else:
                    action=np.random.randint(0,ACTION_SIZE)
                task.offload(action)
                actions.append(action)
            # 作出决策后得到的奖励以及下一步状态
            next_states=env.step(tasks)
            r=env.get_reward()
            #print('r=',r)
            R+=r
            # 将(s,a,s',r)传入经验池
            new_memory=[current_states,actions,next_states,r]
            dqnAgent.add_memory(new_memory)
            # 调用网络训练
            env.current_time+=1
            #dqnAgent.train(env.end())
            # 切换当前状态
            current_states=next_states
        print('R=',R)
        # epsilon衰减
        if EPSILON>MIN_EPSILON:
            EPSILON*=0.05
            EPSILON=max(EPSILON, MIN_EPSILON)




