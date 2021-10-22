from task import Task
from node import *
from collections import deque
import math
from constants import *

class Env:
    def __init__(self):
        # 系统设备状况
        self.transmitStore=TransmitStore
        self.mobileNum=MOBILE_NUM
        self.mecNum=MEC_NUM
        self.mobiles=list()
        self.mecs=list()
        for i in range(self.mobileNum):
            self.mobiles.append(Mobile("mobile"+str(i),"1.1.1."+str(i),{"mem":4}, 2))
        for i in range(self.mecNum):
            self.mecs.append(MEC("mec"+str(i),"1.1.2."+str(i), {"mem":16}, 3))
        # 时隙设定
        self.interval=1
        self.timeSlots=100
        self.currentTime=0
        # 信道带宽-MHz，信噪比-db
        self.bandwidth=20
        self.SNR=10
        # 执行功率 传输功率
        self.processPower=50
        self.transmitPower=20
        # 平衡系数
        self.W1=0.5
        self.W2=1-self.W1

    def reset(self):
        self.currentTime=0
        for mobile in self.mobiles:
            mobile.processQueue.clear()
            mobile.resourceAvil["mem"]=4
        for mec in self.mecs:
            mec.processQueue.clear()
            mec.total_compdelay=0
            mec.resourceAvil["mem"]=16
        self.transmitStore.storeQueue.clear()

    def create_tasks(self):
        tasks=list()
        for i in range(self.mobileNum):
            tasks.append(self.mobiles[i].createTask(self.currentTime))
        return tasks

    def createAllTasks(self):
        allTasks=list()
        for i in range(self.timeSlots):
            tasks=list()
            for j in range(self.mobileNum):
                tasks.append(self.mobiles[j].createTask(i))
            allTasks.append(tasks)
        return allTasks

    def step(self,tasks):
        for task in tasks:
            if task.offload_action==0:
                self.mobiles[int(task.node_from[-1])].updateByTime(task, self.currentTime, 'c', self.get_transpeed(), self.transmitStore.store_queue)
            else:
                self.mobiles[int(task.node_from[-1])].updateByTime(task, self.currentTime, 't', self.get_transpeed(), self.transmitStore.store_queue)
                self.mecs[task.offload_action-1].updateByTime(self.currentTime, self.transmitStore.store_queue)
        next_states=[]
        for mobile in self.mobiles:
            next_states.append([mobile.total_compdelay,mobile.total_trandelay,self.mecs[0].total_compdelay,self.mecs[1].total_compdelay])
        return next_states

    def end(self):
        if self.currentTime>self.timeSlots:
            return True
        return False

    def get_reward(self):
        total_delay=0
        total_consume=0
        for mobile in self.mobiles:
            total_delay=max(mobile.total_compdelay,total_delay)
            total_consume+= self.processPower * mobile.total_compdelay + self.transmitPower * mobile.total_trandelay
        for mec in self.mecs:
            total_delay=max(mec.total_compdelay,total_delay)
            total_consume+= self.processPower * mec.total_compdelay
        return -self.W1*total_delay-self.W2*total_consume

    def get_transpeed(self):
        return self.bandwidth*math.log(1+self.SNR,2)











