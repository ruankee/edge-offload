from collections import deque
import random
from task import Task

class TranStore:
    def __init__(self):
        self.store_queue=deque()

class Mobile:
    def __init__(self,node_id,ip_addr,res_avil,comp_cap):
        self.node_id=node_id
        self.ip_addr=ip_addr
        self.comp_cap=comp_cap
        self.res_avil=res_avil
        self.comp_queue=deque()
        self.total_compdelay=0
        self.tran_queue=deque()
        self.total_trandelay=0
    # 随机生成任务
    def create_task(self,current_time):
        if random.uniform(0,1)>=0.5:
            data_size=random.randint(0,1000)
            tlr_time=random.uniform(3,5)
            mem_req=random.uniform(0,8)
            cpu_req=random.randint(0,1000)
            return Task(current_time,data_size,tlr_time,{"mem_req":mem_req,"cpu_req":cpu_req},self.node_id)
        return Task(0,0,0,{"mem_req":0,"cpu_req":0},self.node_id)
    #
    def updatebytime(self,task,current_time,flag,tran_speed,store_queue):
        if task.data_size==0:
            return
        if flag=='c':
            if len(self.comp_queue)>0 and self.comp_queue[0].end_timestamp==current_time:
                self.comp_queue.pop()
            if task.tlr_time>=max(self.total_compdelay,current_time)-current_time:
                self.comp_queue.append(task)
                if len(self.comp_queue)==0:
                    task.end_timestamp=current_time+get_compdelay(task,self.comp_cap)-1
                else:
                    task.end_timestamp=self.comp_queue[-1].end_timestamp+get_compdelay(task,self.comp_cap)-1
                self.total_compdelay=task.end_timestamp
        else:
            if len(self.tran_queue)==0:
                self.total_trandelay=current_time
            if len(self.tran_queue)>0 and get_trandelay(tran_speed,self.tran_queue[0])<=current_time-self.tran_queue[0].tid+1:
                store_queue.append(self.tran_queue.pop())
            if task.tlr_time>=self.total_trandelay-current_time:
                self.tran_queue.append(task)
                task.tran_timestamp=self.tran_queue[-1].tran_timestamp+get_trandelay(tran_speed,self.tran_queue[0])-1
                self.total_trandelay=task.tran_timestamp

class MEC:
    def __init__(self,node_id,ip_addr,res_avil,comp_cap):
        self.node_id=node_id
        self.ip_addr=ip_addr
        self.comp_cap=comp_cap
        self.res_avil=res_avil
        self.comp_queue=deque()
        self.total_compdelay=0
    #
    def updatebytime(self,current_time,store_queue):
        if len(self.comp_queue)==0:
            self.total_compdelay=current_time
        if len(self.comp_queue)>0 and self.comp_queue[0].end_timestamp==current_time:
            self.comp_queue.pop()
        for task in store_queue:
            if str(task.offload_action+1)==self.node_id[-1]:
                if current_time<=task.tran_timestamp<current_time+1:
                    if len(self.comp_queue)>0 and self.comp_queue[0].end_timestamp==current_time:
                        self.comp_queue.pop()
                    if task.tlr_time>=max(self.total_compdelay,current_time)-current_time:
                        self.comp_queue.append(task)
                        if len(self.comp_queue)==0:
                            task.end_timestamp=current_time+get_compdelay(task,self.comp_cap)-1
                        else:
                            task.end_timestamp=self.comp_queue[-1].end_timestamp+get_compdelay(task,self.comp_cap)-1
                        self.total_compdelay=task.end_timestamp
                    store_queue.pop()
                else:
                    break

# 执行时延
def get_compdelay(task,comp_cap):
    return task.rs_req["cpu_req"]/comp_cap
# 传输时延
def get_trandelay(tran_speed,task):
    return task.data_size/tran_speed


