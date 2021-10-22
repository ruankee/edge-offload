from node import *
import math
from constants import *

class Env:
    def __init__(self):
        # 系统设备状况
        self.transmitStore=TransmitStore()
        self.mobileNum=MOBILE_NUM
        self.mecNum=MEC_NUM
        self.mobiles=list()
        self.mecs=list()
        for i in range(self.mobileNum):
            self.mobiles.append(Mobile("mobile"+str(i),"1.1.1."+str(i),{"mem":4}))
        for i in range(self.mecNum):
            self.mecs.append(MEC("mec"+str(i),"1.1.2."+str(i), {"mem":16}))
        # 时隙设定
        self.interval=0.1
        self.timeSlots=10
        self.currentTime=0
        # 信道带宽-MHz，信噪比-db
        self.bandwidth=50
        self.SNR=10

    def reset(self):
        self.currentTime=0
        for mobile in self.mobiles:
            mobile.processQueue.clear()
            mobile.resourceAvil["mem"]=4
        for mec in self.mecs:
            mec.processQueue.clear()
            mec.resourceAvil["mem"]=16
        self.transmitStore.storeQueue.clear()

    def createTasks(self):
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
        transmitSpeed=self.getTransmitSpeed()
        for task in tasks:
            if task.offloadAction==0:
                self.mobiles[int(task.nodeFrom[-1])].updateByTime(task,self.currentTime,self.interval,self.transmitStore.storeQueue,transmitSpeed)
            else:
                self.mobiles[int(task.nodeFrom[-1])].updateByTime(task,self.currentTime,self.interval,self.transmitStore.storeQueue,transmitSpeed)
                self.mecs[task.offloadAction-1].updateByTime(self.currentTime, self.interval,self.transmitStore.storeQueue)

    def end(self):
        if self.timeSlots<self.currentTime<=self.timeSlots+self.interval:
            return True
        return False

    def getTransmitSpeed(self):
        return self.bandwidth*math.log(1+self.SNR,2)

    def getMECLoad(self):
        MECLoad=[0,0]
        for i in range(len(self.mecs)):
            load=0
            for task in self.mecs[i].processQueue:
                load+=task.dataSize
            MECLoad[i]=load
        return MECLoad










