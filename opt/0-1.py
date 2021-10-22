import pulp      # 导入 pulp 库

# 主程序
def main():
    # 投资决策问题：
    # 公司现有 5个拟投资项目，根据投资额、投资收益和限制条件，问如何决策使收益最大。
    """
    问题建模：
        决策变量：
            x1～x5：0/opt 变量，opt 表示选择第 i 个项目， 0 表示不选择第 i 个项目
        目标函数：
            max fx = 150*x1 + 210*x2 + 60*x3 + 80*x4 + 180*x5
        约束条件：
            210*x1 + 300*x2 + 100*x3 + 130*x4 + 260*x5 <= 600
            x1 + x2 + x3 = opt
            x3 + x4 <= opt
            x5 <= x1
            x1,...,x5 = 0, opt
    """
    InvestLP = pulp.LpProblem("Invest decision problem", sense=pulp.LpMaximize)  # 定义问题，求最大值
    x1 = pulp.LpVariable('A', cat='Binary')  # 定义 x1，A 项目
    x2 = pulp.LpVariable('B', cat='Binary')  # 定义 x2，B 项目
    x3 = pulp.LpVariable('C', cat='Binary')  # 定义 x3，C 项目
    x4 = pulp.LpVariable('D', cat='Binary')  # 定义 x4，D 项目
    x5 = pulp.LpVariable('E', cat='Binary')  # 定义 x5，E 项目
    InvestLP += (150*x1 + 210*x2 + 60*x3 + 80*x4 + 180*x5)  # 设置目标函数 f(x)
    InvestLP += (210*x1 + 300*x2 + 100*x3 + 130*x4 + 260*x5 <= 600)  # 不等式约束
    InvestLP += (x1 + x2 + x3 == 1)  # 等式约束
    InvestLP += (x3 + x4 <= 1)  # 不等式约束
    InvestLP += (x5 - x1 <= 0)  # 不等式约束
    InvestLP.solve()
    print(InvestLP.name)  # 输出求解状态
    print("Status youcans:", pulp.LpStatus[InvestLP.status])  # 输出求解状态
    for v in InvestLP.variables():
        print(v.name, "=", v.varValue)  # 输出每个变量的最优值
    print("Max f(x) =", pulp.value(InvestLP.objective))  # 输出最优解的目标函数值

    return

if __name__ == '__main__':  # Copyright 2021 YouCans, XUPT
    main()  # Python小白的数学建模课 @ Youcans
