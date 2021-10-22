# import gym
# import numpy as np
import random
# env = gym.make("CartPole-v0")
# env.reset()
# print(env.observation_space.shape)
#
# print(np.array([1,1,1,1]).shape)
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
# EPSILON=0.9
# MIN_EPSILON=0.1
# for i in range(250):
#     if EPSILON > MIN_EPSILON:
#         EPSILON -= EPSILON * 0.02
#         EPSILON = max(EPSILON, MIN_EPSILON)
#         print(EPSILON)
#         plt.scatter(i,EPSILON)
# plt.show()
# import math
# print(50*math.log(1+10,2))
a=deque()
for i in range(1,11):
    a.append(i)
while len(a)>3 and a[-1]>4:
    a.pop()
try:
    if a.index(9)>-1:
        print('9 存在')
except ValueError:
    print('ok')
#
# b=list()
# # print(len(b))
# def x():
#     a=1
#     b=4
#     return (a-b) if a-b>0 else 0
# print(x())

