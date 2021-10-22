from task import Task
from node import *
from collections import deque
import math

class Env:
    def __init__(self):
        # 系统设备状况
        self.tran_store=TranStore()
        self.mobile_num=10
        self.mec_num=2
        self.mobiles=list()
        self.mecs=list()
        for i in range(self.mobile_num):
            self.mobiles.append(Mobile("mobile"+str(i),"1.1.1."+str(i),{"mem":4}, 50))
        for i in range(self.mec_num):
            self.mecs.append(MEC("mec"+str(i),"1.1.2."+str(i), {"mem":16}, 100))
        # 时隙设定
        self.interval=1
        self.time_slots=50
        self.current_time=0
        # 信道带宽-MHz，信噪比-db
        self.bandwidth=20
        self.SNR=10
        # 执行功率 传输功率
        self.comp_p=50
        self.tran_p=20
        # 平衡系数
        self.W1=0.5
        self.W2=1-self.W1

    def reset(self):
        self.current_time=0
        for mobile in self.mobiles:
            mobile.comp_queue.clear()
            mobile.comp_delay=0
            mobile.tran_delay=0
            mobile.res_avil["mem"]=4
        for mec in self.mecs:
            mec.comp_queue.clear()
            mec.comp_delay=0
            mec.res_avil["mem"]=16

    def create_tasks(self):
        tasks=list()
        for i in range(self.mobile_num):
            tasks.append(self.mobiles[i].create_task(self.current_time))
        return tasks

    def step(self,tasks):
        for task in tasks:
            if task.offload_action==0:
                self.mobiles[int(task.node_from[-1])].updatebytime(task,self.current_time,'c',self.get_transpeed(),self.tran_store.store_queue)
            else:
                self.mobiles[int(task.node_from[-1])].updatebytime(task,self.current_time,'t',self.get_transpeed(),self.tran_store.store_queue)
                self.mecs[task.offload_action-1].updatebytime(self.current_time,self.tran_store.store_queue)
        next_states=[]
        for mobile in self.mobiles:
            next_states.append([mobile.total_compdelay,mobile.total_trandelay,self.mecs[0].total_compdelay,self.mecs[1].total_compdelay])
        return next_states
        #     # 本地执行
        #     if task.node_to==0:
        #         # 任务进入执行队列
        #         self.mobiles[task.node_from].comp_queue.append(task)
        #         self.mobiles[task.node_from].set_compdelay(task)
        #     # 边缘执行
        #     else:
        #         self.mobiles[task.node_from].tran_queue.append(task)
        #         self.mecs[task.offload_action].comp_queue.append(task)
        #         self.mobiles[task.node_from].set_trandelay(self.bandwidth*math.log(1+self.SNR,2),task)
        #         self.mecs[task.offload_action].set_compdelay(task,self.mobiles[task.node_from].tran_delay)

    def end(self):
        if self.current_time>self.time_slots:
            return True
        return False

    def get_reward(self):
        total_delay=0
        total_consume=0
        for mobile in self.mobiles:
            total_delay=max(mobile.total_compdelay,total_delay)
            total_consume+=self.comp_p*mobile.total_compdelay+self.tran_p*mobile.total_trandelay
        for mec in self.mecs:
            total_delay=max(mec.total_compdelay,total_delay)
            total_consume+=self.comp_p*mec.total_compdelay
        return -self.W1*total_delay-self.W2*total_consume

    def get_transpeed(self):
        return self.bandwidth*math.log(1+self.SNR,2)











