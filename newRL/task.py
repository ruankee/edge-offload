class Task:
    """
        arriveTime-到达时间

    """
    def __init__(self,arriveTime,dataSize,resourceReq,nodeFrom):
        self.arriveTime = arriveTime
        self.dataSize = dataSize
        self.resourceReq = resourceReq
        #self.tolerateDuration = tolerateDuration
        self.nodeFrom = nodeFrom
        self.processDelay = 0
        self.processedTime = 0
        self.transmitDelay= 0
        self.transmittedTime = 0
        self.offloadAction = 0
    # 该任务卸载去向
    def setOffloadAction(self,action):
        self.offloadAction = action


