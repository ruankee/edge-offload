class Task:
    # tid:以到达时隙为本机任务标识
    # data_size:任务数据量大小
    # tlr_time:任务容忍时间
    # rs_req:资源需求集合，包括cpu周期数、内存大小等
    # node_from:任务所来自节点
    # offload_action:任务执行所在节点
    def __init__(self,tid,data_size,tlr_time,rs_req,node_from):
        self.tid=tid
        self.data_size=data_size
        self.tran_timestamp=0
        self.end_timestamp=0
        self.tlr_time=tlr_time
        self.rs_req=rs_req
        self.node_from=node_from
        self.offload_action=0
    # 该任务卸载去向
    def offload(self,action):
        self.offload_action=action

