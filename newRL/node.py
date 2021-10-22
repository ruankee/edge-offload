from collections import deque
import random
from task import Task

class TransmitStore:
    def __init__(self):
        self.storeQueue=deque()

class Mobile:
    def __init__(self,nodeId,ipAddr,resourceAvil):
        self.nodeId = nodeId
        self.ipAddr = ipAddr
        self.cpuCapacity = 2
        self.resourceAvil = resourceAvil
        # 执行功率 传输功率
        self.processPower = 15
        self.transmitPower = 8
        self.processQueue = deque()
        self.transmitQueue = deque()
    # 随机生成任务
    def createTask(self,currentTime):
        if random.uniform(0,1)>=0.5:
            dataSize = random.randint(0,500)
            #tolerateDuration = random.uniform(3,5)
            memReq =  random.uniform(0,8)
            cpuReq = random.randint(0,1000)
            return Task(currentTime,dataSize,{"memReq":memReq,"cpuReq":cpuReq}, self.nodeId)
        return Task(0,0,{"memReq":0,"cpuReq":0},self.nodeId)
#
    def updateByTime(self,task,currentTime,interval,storeQueue,transmitSpeed):
        if task.dataSize>0:
            if task.offloadAction==0:
                task.processDelay=getProcessDelay(task,self.cpuCapacity)
                task.processedTime=getQueueWaitDelay(currentTime,self.processQueue)+task.processDelay
                self.processQueue.append(task)
            else:
                task.transmitDelay=getTransmitDelay(task,transmitSpeed)
                task.transmittedTime=getQueueWaitDelay(currentTime,self.transmitQueue)+task.transmitDelay
                self.transmitQueue.append(task)
        while len(self.processQueue)>0 and currentTime-interval< self.processQueue[-1].processedTime <=currentTime:
            self.processQueue.pop()
        while len(self.transmitQueue)>0 and currentTime-interval< self.transmitQueue[-1].transmittedTime <=currentTime:
            storeQueue.append(self.transmitQueue.pop())
class MEC:
    def __init__(self,nodeId,ipAddr,resourceAvil):
        self.nodeId = nodeId
        self.ipAddr = ipAddr
        self.cpuCapacity = 8
        self.resourceAvil = resourceAvil
        # 执行功率 传输功率
        self.processPower = 55
        self.processQueue = deque()
#
    def updateByTime(self,currentTime,interval,storeQueue):
        popTasks=list()
        for task in storeQueue:
            if task.transmittedTime>currentTime:
                break
            else:
                if str(task.offloadAction-1)==self.nodeId[-1]:
                    task.processDelay=getProcessDelay(task,self.cpuCapacity)
                    task.processedTime=getQueueWaitDelay(currentTime,self.processQueue)+task.processDelay
                    while len(self.processQueue)>0 and currentTime-interval< self.processQueue[-1].processedTime <=currentTime:
                        self.processQueue.pop()
                    self.processQueue.append(task)
                    popTasks.append(task)
        for task in popTasks:
            storeQueue.remove(task)

def getQueueWaitDelay(currentTime,nQueue):
    if len(nQueue)==0:
        return 0
    else:
        return nQueue[-1].processedTime-currentTime if nQueue[-1].processedTime-currentTime>0 else 0
# 执行时延
def getProcessDelay(task,cpuCapacity):
    return task.resourceReq["cpuReq"]/cpuCapacity

# 传输时延
def getTransmitDelay(task,transmitSpeed):
    return task.dataSize/transmitSpeed




