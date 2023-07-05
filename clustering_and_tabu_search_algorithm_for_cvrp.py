# -*- coding: utf-8 -*-
"""Clustering and Tabu search algorithm for CVRP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14SOIlrzFIzXar7oan-3cYVxw1nXeN5pb

# **0. 패키지 및 데이터 다운로드**
"""

!pip install haversine

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

import random
import timeit

import warnings
warnings.filterwarnings(action='ignore')

from haversine import haversine
import sklearn
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering

from google.colab import files
files.upload()

"""# **1. 데이터 불러오기 및 전처리**"""

sample_data_0 = pd.read_excel('sample_data_1.xlsx')
sample_data_1 = sample_data_0.drop('Unnamed: 0', axis=1)
sample_data_2 = sample_data_1.drop('Unnamed: 0.1', axis=1)
sample_data_3 = sample_data_2.drop('index', axis=1)
sample_data_4 = sample_data_3.reset_index()

sample4_L = sample_data_4['latitude']
sample4_H = sample_data_4['longitude']
sample4_location = []

for i in range(len(sample_data_4)):
  for j in range(len(sample_data_4)):
    start = (float(sample4_L[i]), float(sample4_H[i]))
    goal = (float(sample4_L[j]), float(sample4_H[j]))
    path_distance = haversine(start, goal)
    sample4_location.append(path_distance)

sample4_distance = np.reshape(sample4_location, (len(sample_data_4), len(sample_data_4)))

"""# **2. 클러스터링 알고리즘 실행**"""

model = shc.linkage(sample4_distance, method='ward', metric='euclidean')

plt.figure(figsize = (16,10))
plt.title("Customer Clustering Process")
graph = shc.dendrogram(model)

print(graph)

k = 4
ab = AgglomerativeClustering(n_clusters = k, affinity = 'euclidean', linkage = 'ward')
labels = ab.fit_predict(sample4_distance)

sample_data_4['cluster'] = labels
N = []

for j in range(k+1):
  n_sum = 0
  for i in range(len(sample_data_4)):
    if sample_data_4['cluster'][i] == j:
      n_sum = n_sum + sample_data_4['Number'][i]
  N.append(n_sum)


N.remove(0)
print(N)

sample_data_4['cluster'].value_counts()

plt.figure(figsize = (8, 8))

for i in range(k):
  if i in sample_data_4['cluster']:
    plt.scatter(sample_data_4.loc[sample_data_4['cluster'] == i, 'longitude'],
                sample_data_4.loc[sample_data_4['cluster'] == i, 'latitude'],
                label = 'cluster' + str(i))

plt.scatter(127.070490, 37.496426, marker = '*', s = 300, label = 'hub')

plt.legend(bbox_to_anchor=(1,1))
plt.title('A = %d results'%k , size = 15)
plt.xlabel('longitude', size = 12)
plt.ylabel('latitude', size = 12)
plt.show()

"""# **3. Tabu Search 알고리즘 실행**

(1) 데이터 불러오기 및 전처리
"""

df_all = sample_data_4

dis_V = pd.read_excel('sample_distance_asis_1.xlsx')

N_cus = len(df_all)
N_sta = 0

vehicle_capacity = 1100
vehicle_number = len(df_all['cluster'].unique())
speed = [8.33 for i in range(vehicle_number)] # m/s^2 == [30km/h]
vehicle_capa = 1100 # kg
weight = [1080 for i in range(vehicle_number)] # kg

vehicle_number

t=[]

for k in range(len(df_all)):
  for i in range(len(sample_data_4)):
      if i == df_all['index'][k]:
        t.append(i)

t.append(len(sample_data_4))

dis_2 = []

for i in range(len(t)):
  for j in range(len(t)):
    dis_2.append(dis_V[t[j]][t[i]])

dis_reshape2 = np.reshape(dis_2, (len(t), len(t)))
disDF_V = pd.DataFrame(dis_reshape2)
dist_V = disDF_V.reset_index()

start_time = timeit.default_timer()
iteration_number = 50
initial_number = 100
candidate_number = 5
inner_loop = 50

load_capacity = [1100, 1100] # kg

neighbor_number = 30
tabu_number = 8

route = []
route_all = [[] for i in range(vehicle_number)]
vehicle_route = [[] for i in range(vehicle_number)]
vehicle_dist = []
comparison = []
load = []
node = []
allocation = []
check1 = [[] for a in range(vehicle_number)] # station이 들어갈 위치
check2 = [[] for a in range(vehicle_number)] # 사용된 station 번호
check_X = []
load_tabu = [[[] for i in range(vehicle_number)] for i in range(neighbor_number)]

incumbent_solution = [[] for i in range(vehicle_number)]
incumbent_value = []
initial_solution = [[[] for i in range(vehicle_number)] for i in range(initial_number)]
initial_value = []

neighbor = [[[] for i in range(vehicle_number)] for i in range(neighbor_number)]
neighbor_obj = []

tabu_table = []
for i in range(tabu_number):
    tabu_table.append(0)

neighbor_move = [[] for i in range(neighbor_number)]
penalty = [[] for i in range(neighbor_number)]
penalty2 = []
candidate_solution = [[[] for i in range(vehicle_number)] for i in range(candidate_number)]
candidate_value = []
candidate_source = []
temp_chunk = []
check_swift_4 = []

"""(2) 초기해 생성 함수"""

def initial_1(check_X, node, allocation, route_all):
    check_X.clear()
    node.clear()
    comparison.clear()
    route_all.clear()

    for i in range(len(route_all)):
        route_all[i].clear()

    for i in range(N_cus):
        node.append(i+1)

    allocation.clear()
    #print(len(node))
    #print(node)
    ###########################################################################################
    xy = []
    for y in range(len(df_all['cluster'].unique())):

      x_lat = 37.182769
      y_lat = df_all[df_all['cluster'] == y]['latitude'].mean()
      x_lon = 127.327603
      y_lon = df_all[df_all['cluster'] == y]['longitude'].mean()

      start_x = (x_lat, x_lon)
      goal_y = (y_lat, y_lon)

      xy_path_distance = haversine(start_x, goal_y)
      xy.append(xy_path_distance)

    xy.sort()
    #print(xy)

    yz = []
    for z in range(len(df_all['cluster'].unique())):

      x_lat = 37.182769
      y_lat = df_all[df_all['cluster'] == z]['latitude'].mean()
      x_lon = 127.327603
      y_lon = df_all[df_all['cluster'] == z]['longitude'].mean()

      start_x = (x_lat, x_lon)
      goal_y = (y_lat, y_lon)

      yz_path_distance = haversine(start_x, goal_y)
      yz.append(yz_path_distance)
    #print(yz)

    sort = []

    for j in range(len(yz)):
      if xy[0] == yz[j]:
        sort.append(j)
    #print(sort)

    for a in range(len(df_all['cluster'].unique())-1):
      xy_1 = []
      for y in range(len(df_all['cluster'].unique())):
        if y not in sort:

          x_lat = df_all[df_all['cluster'] == sort[a]]['latitude'].mean()
          y_lat = df_all[df_all['cluster'] == y]['latitude'].mean()
          x_lon = df_all[df_all['cluster'] == sort[a]]['longitude'].mean()
          y_lon = df_all[df_all['cluster'] == y]['longitude'].mean()

          start_x = (x_lat, x_lon)
          goal_y = (y_lat, y_lon)

          xy_path_distance = haversine(start_x, goal_y)
          xy_1.append(xy_path_distance)

        else:
          xy_1.append(0)

        xy_1.sort()
      #print("xy_1: ", xy_1)

      yz_1 = []
      for z in range(len(df_all['cluster'].unique())):
        if z not in sort:

          x_lat = df_all[df_all['cluster'] == sort[a]]['latitude'].mean()
          y_lat = df_all[df_all['cluster'] == z]['latitude'].mean()
          x_lon = df_all[df_all['cluster'] == sort[a]]['longitude'].mean()
          y_lon = df_all[df_all['cluster'] == z]['longitude'].mean()

          start_x = (x_lat, x_lon)
          goal_y = (y_lat, y_lon)

          yz_path_distance = haversine(start_x, goal_y)
          yz_1.append(yz_path_distance)

        else:
          yz_1.append(0)
      #print('yz_1: ', yz_1)

      for j in range(len(yz_1)):
        if xy_1[a+1] == yz_1[j]:
          sort.append(j)
    #print('sort: ', sort)
    ###########################################################################################
    x = len(df_all['cluster'].unique())

    for i in range(x):
        a = len(df_all.loc[df_all['cluster'] == sort[i]])
        allocation.append(a)
    #print(allocation)
    ###########################################################################################
    random_route = [[] for i in range(len(df_all['cluster'].unique()))]

    for i in range(len(df_all['cluster'].unique())):
      for j in range(len(node)):
        if df_all['cluster'][node[j]-1] == sort[i]:
          random_route[i].append(node[j])
    #print(random_route)
    #print("")

    for i in range(len(df_all['cluster'].unique())):
      random.shuffle(random_route[i])
      route_all.append(random_route[i])
    #print(route_all)

    check_X.append(1)


def initial_2(check_X, load, route_all):
    check_X.clear()
    load.clear()
    u=0
    for i in range(len(route_all)):
        sum_De = 0
        sum_Re = 0
        for j in range(len(route_all[i])):
            sum_De = sum_De + df_all['De'][route_all[i][j]-1]
            sum_Re = sum_Re + df_all['Re'][route_all[i][j]-1]
        load.append(sum_De)
        if sum_De > vehicle_capa:
            check_X.append(0)
        elif sum_Re > vehicle_capa:
            check_X.append(0)
        else:
            check_X.append(1)

    for i in check_X:
        if 0 in check_X:
            check_X.clear()
            check_X.append(0)
            break
        else:
            check_X.clear()
            check_X.append(1)



def initial_3(check_X, comparison, route_all):

    comparison.clear()

    # Greedy를 이용한 초기 경로 생성 - step 3
    for i in range(len(route_all)):
        if vehicle_capa == 1100:

            # 경로의 첫 노드 결정
            for j in range(len(route_all[i])):
                dist = dist_V[N_cus][route_all[i][j]-1]
                comparison.append(dist)
            comparison.sort()
            #print(comparison)

            for j in range(len(route_all[i])):
                if comparison[0] == dist_V[N_cus][route_all[i][j]-1]:
                    temp = route_all[i][0]
                    route_all[i][0] = route_all[i][j]
                    route_all[i][j] = temp
            comparison.clear()

            # 경로의 n번째 노드 결정(n>=2)
            k = 0
            while k < len(route_all[i])-1:

                for j in range(k,len(route_all[i])-1):
                    dist = dist_V[route_all[i][k]-1][route_all[i][j+1]-1]
                    comparison.append(dist)
                comparison.sort()

                for j in range(k,len(route_all[i])-1):
                    if comparison[0] == dist_V[route_all[i][k]-1][route_all[i][j+1]-1]:
                        temp = route_all[i][k+1]
                        route_all[i][k+1] = route_all[i][j+1]
                        route_all[i][j+1] = temp
                comparison.clear()
                k = k + 1
    check_X.clear()
    check_X.append(1)


def initial_4(check_X, load, route_all):
    #print(route_all)

    # 싣고 있는 짐의 양 확인 --> Q = sum(De), Q - De + Re <= load_capacity - step 4
    check_X.clear()
    for i in range(vehicle_number):
        #print(vehicle_number)

        # 각 장비의 총 수요량 확인
        Q = load[i]


        # 삼륜차의 적재량 제약 확인
        if vehicle_capa == 1100:
            for j in range(len(route_all[i])):
                #print(len(route_all[i]))
                if Q - df_all['De'][route_all[i][j]-1] + df_all['Re'][route_all[i][j]-1] <= load_capacity[1]:
                    #print(Q)
                    Q = Q - df_all['De'][route_all[i][j]-1] + df_all['Re'][route_all[i][j]-1]
                    #print(Q)
                # 제약 조건 벗어나면 다시 step 1 로 이동
                else:
                    check_X.append(0)
                    break

    check_X.append(1)
    #print("초기해: ",route_all)

"""(3) 거리계산 및 목적함수"""

def f_route(route_all, check1, check2):

    for i in range(vehicle_number):
        vehicle_route[i].clear()

    for i in range(vehicle_number):
        for j in range(len(route_all[i])):
            if len(check1[i]) == 0:
                vehicle_route[i].append(route_all[i][j])
            else:
                if len(check1[i]) == 1:
                    if j == check1[i][0]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][0])
                        vehicle_route[i].append(route_all[i][j])
                    else:
                        vehicle_route[i].append(route_all[i][j])
                elif len(check1[i]) == 2:
                    if j == check1[i][0]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][0])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][1]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][1])
                        vehicle_route[i].append(route_all[i][j])
                    elif j != check1[i][0] or j != check1[i][1]:
                        vehicle_route[i].append(route_all[i][j])
                elif len(check1[i]) == 3:
                    if j == check1[i][0]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][0])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][1]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][1])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][2]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][2])
                        vehicle_route[i].append(route_all[i][j])
                    elif j != check1[i][0] or j != check1[i][1] or j != check1[i][2]:
                        vehicle_route[i].append(route_all[i][j])
                elif len(check1[i]) == 4:
                    if j == check1[i][0]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][0])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][1]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][1])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][2]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][2])
                        vehicle_route[i].append(route_all[i][j])
                    elif j == check1[i][3]:
                        vehicle_route[i].append(N_cus+1+2*check2[i][3])
                        vehicle_route[i].append(route_all[i][j])
                    elif j != check1[i][0] or j != check1[i][1] or j != check1[i][2] or j != check1[i][3]:
                        vehicle_route[i].append(route_all[i][j])

        #vehicle_route[i].insert(0, N_cus+1)
        #vehicle_route[i].append(N_cus+1)
    vehicle_route[0].insert(0, N_cus+1)
    vehicle_route[i].append(N_cus+1)

    return(vehicle_route)


# 거리 측정 함수

def f_dist(vehicle_route):

    vehicle_dist.clear()
    dist = 0
    a = -1

    for i in range(vehicle_number):
        if vehicle_capa == 1100:
            for j in range(len(vehicle_route[i])):
                if j != len(vehicle_route[i])-1:
                    dist = dist + dist_V[vehicle_route[i][j]-1][vehicle_route[i][j+1]-1]
                    a = a+1

                elif j == len(vehicle_route[i])-1 and i != vehicle_number - 1:
                    dist = dist + dist_V[vehicle_route[i][j]-1][vehicle_route[i+1][0]-1]
                    a = a+1
                elif j == len(vehicle_route[i])-1 and i == vehicle_number - 1:
                    break

                #print(a)
                #print(dist)
            vehicle_dist.append(dist)



# incumbent solution / value 기록 함수

def incumbent(vehicle_route, vehicle_dist, incumbent_solution, incumbent_value):

    if len(incumbent_value) == 0:
        total_dist = 0
        for i in range(len(vehicle_dist)):
            total_dist = total_dist + vehicle_dist[i]

        incumbent_value.append(total_dist)
        for i in range(vehicle_number):
            for j in range(len(vehicle_route[i])):
                incumbent_solution[i].append(vehicle_route[i][j])

    else:
        total_dist = 0
        for i in range(len(vehicle_dist)):
            total_dist = total_dist + vehicle_dist[i]
        if len(penalty2) > 0:
            for i in range(len(penalty2)):
                if len(incumbent_value) > 0:
                    total_dist = total_dist + incumbent_value[0]/4
                else:
                    total_dist = total_dist + 50

        if incumbent_value[0] > total_dist:
            incumbent_value.clear()
            incumbent_value.append(total_dist)

            for i in range(vehicle_number):
                incumbent_solution[i].clear()
                for j in range(len(vehicle_route[i])):
                    incumbent_solution[i].append(vehicle_route[i][j])

"""(4) 패널티 함수"""

# penalty 함수 모음

# penalty 1 : 싣고 있는 짐의 양 확인 --> Q = sum(De), Q - De + Re <= load_capacity

def penalty_1(neighbor, neighbor_obj, penalty, incumbent_value):

    for m in range(neighbor_number):
        penalty[m].clear()


    for m in range(neighbor_number):
        for i in range(vehicle_number):

            # 각 장비의 총 수요량 확인

            load_tabu[m][i].clear()

            sum_De = 0
            for x in range(len(neighbor[m][i])):
                if neighbor[m][i][x] < N_cus+1:
                    sum_De = sum_De + df_all['De'][neighbor[m][i][x]-1]
            load_tabu[m][i].append(sum_De)
            Q = load_tabu[m][i][0]


            # 삼륜차의 적재량 제약 확인
            if vehicle_capa == 1100:
                for j in range(1,len(neighbor[m][i])-1):
                    if neighbor[m][i][j] < N_cus+1:
                        if Q - df_all['De'][neighbor[m][i][j]-1] + df_all['Re'][neighbor[m][i][j]-1] <= load_capacity[1]:
                            Q = Q - df_all['De'][neighbor[m][i][j]-1] + df_all['Re'][neighbor[m][i][j]-1]

                        # 제약 조건 벗어나면 penalty 추가
                        else:
                            obj_save = neighbor_obj[m] + incumbent_value[0]/4
                            del neighbor_obj[m]
                            neighbor_obj.insert(m, obj_save)
                            penalty[m].append(1)


# penalty 2 : De, Re 확인

def penalty_2(neighbor, neighbor_obj, penalty, incumbent_value):

    for m in range(neighbor_number):

        if check_swift_4[m] == 1:
            for i in range(len(neighbor[m])):
                sum_De = 0
                sum_Re = 0
                for j in range(len(neighbor[m][i])):
                    if neighbor[m][i][j] < N_cus+1:
                        sum_De = sum_De + df_all['De'][neighbor[m][i][j]-1]
                        sum_Re = sum_Re + df_all['Re'][neighbor[m][i][j]-1]


                if sum_De > vehicle_capa:
                    obj_save = neighbor_obj[m] + incumbent_value[0]/4
                    del neighbor_obj[m]
                    neighbor_obj.insert(m, obj_save)
                    penalty[m].append(1)
                    break
                elif sum_Re > vehicle_capa:
                    obj_save = neighbor_obj[m] + incumbent_value[0]/4
                    del neighbor_obj[m]
                    neighbor_obj.insert(m, obj_save)
                    penalty[m].append(1)
                    break

"""(5) 노드 변경 함수"""

# 노드 변경 알고리즘 모음

# 변경 알고리즘 1 - 두개 노드 선택해서 위치 변경

def swift_1(vehicle_route, i, j):

    # 1) 노드만 2개 변경

    b = 1
    neighbor[i][j].clear()

    for X in range(b):

        a = random.randint(1,len(vehicle_route[j])-2)
        x = 0
        while x < 1:
            if len(vehicle_route[j]) == 3:
                b = 1
                break
            elif len(vehicle_route[j]) > 3:
                b = random.randint(1,len(vehicle_route[j])-2)
            if a == b:
                continue
            x = 1


        for k in range(len(vehicle_route[j])):
            neighbor[i][j].append(vehicle_route[j][k])

        neighbor_move[i].clear()
        neighbor_move[i].append(neighbor[i][j][a])
        neighbor_move[i].append(neighbor[i][j][b])

        temp = neighbor[i][j][a]
        neighbor[i][j][a] = neighbor[i][j][b]
        neighbor[i][j][b] = temp




# 2) chuck 로 노드 변경 (2개 이상, x개 이하의 연속된 노드, 뒤에 붙이는 것이 아니라 랜덤의 위치에 붙이기 )

def swift_2(vehicle_route, i, j, temp_chunk):

    if len(vehicle_route[j]) >= 5:
        # chunk 개수
        a = random.randint(2, len(vehicle_route[j])-3)
        # chunk 자르는 위치
        b = random.randint(1, len(vehicle_route[j])-a-1)

        temp_chunk.clear()
        neighbor[i][j].clear()

        for k in range(len(vehicle_route[j])):
            neighbor[i][j].append(vehicle_route[j][k])

        for k in range(a):
            temp_chunk.append(neighbor[i][j][b+k])

        for k in range(a):
            del neighbor[i][j][b]

        # chunk 붙이는 위치
        del neighbor[i][j][-1]
        c = random.randint(1,len(neighbor[i][j]))
        for k in range(a):
            neighbor[i][j].insert(c+k,temp_chunk[k])
        neighbor[i][j].append(N_cus+1)

        neighbor_move[i].clear()
        neighbor_move[i].append(temp_chunk[0])
        neighbor_move[i].append(temp_chunk[1])


# 3) 노드 1개만 경로 중간에 끼워넣기

def swift_3(vehicle_route, i, j):

    if len(vehicle_route[j]) > 3:

        neighbor_move[i].clear()
        neighbor[i][j].clear()

        for k in range(len(vehicle_route[j])):
            neighbor[i][j].append(vehicle_route[j][k])

        #b = random.randint(1,3)
        b=1
        for X in range(b):

            a = random.randint(1, len(vehicle_route[j])-2)
            c = random.randint(1, len(vehicle_route[j])-2)

            temp = neighbor[i][j][a]
            del neighbor[i][j][a]
            neighbor[i][j].insert(c, temp)

            neighbor_move[i].append(temp)
            neighbor_move[i].append(neighbor[i][j][c-1])

"""(6) 이웃해 생성, 평가, 그리고 탐색 함수"""

# tabu search 를 통해 해의 개선

# 이웃해 생성 및 평가
def tabu_1(neighbor, neighbor_obj, vehicle_route):

    check_swift_4.clear()

    for i in range(neighbor_number):

        #################################################################
        # 이웃해 성성 방법 2가지 : 노드 방문 순서 변경 / station의 변경 또는 station의 추가
        #1) 노드 2개 선택하여 변경  2) 노드를 chunk로 변경  3)

        # 경로에 포함된 노드의 수가 많을수록 선택확률이 높게 설정
        sum_node = 0
        for k in range(vehicle_number):
            sum_node = sum_node + (len(vehicle_route[k])-2)

        select_val = random.randint(1,sum_node)
        sum_node = 0
        k = 0
        while k < (vehicle_number):
            sum_node = sum_node + (len(vehicle_route[k])-2)
            if select_val <= sum_node:
                j = k
                k = vehicle_number
                break
            k = k + 1

        for k in range(vehicle_number):
            neighbor[i][k].clear()


        n = [0, 1, 2]

        a = np.random.choice(n, 1, p=[0.33, 0.33, 0.34])


        if a == 4:
            check_swift_4.append(1)
        else:
            check_swift_4.append(0)

        # 1) 노드만 2개 변경

        if a == 0:
            swift_1(vehicle_route, i, j)


        # 2) chuck 로 노드 변경 (2개 이상, x개 이하의 연속된 노드, 뒤에 붙이는 것이 아니라 랜덤의 위치에 붙이기 )

        elif a == 1:

            swift_2(vehicle_route, i, j, temp_chunk)


        # 3) 노드 1개만 경로 중간에 끼워넣기

        elif a == 2:

            swift_3(vehicle_route, i, j)


        #print("neighbor_move[i]: ",neighbor_move[i])



    # 안 바뀐 부분 다시 neighbor에 넣기

    for i in range(neighbor_number):
        for j in range(vehicle_number):
            if len(neighbor[i][j]) == 0:
                for k in range(len(vehicle_route[j])):
                    neighbor[i][j].append(vehicle_route[j][k])


    #################################################################
    # 이웃해의 목적함수값 확인
    neighbor_obj.clear()
    for i in range(neighbor_number):
        f_dist(neighbor[i])

        total_dist = 0
        for j in range(len(vehicle_dist)):
            total_dist = total_dist + vehicle_dist[j]

        neighbor_obj.append(total_dist)
    #print("neighbor obj : ",neighbor_obj)
    #print("")

    #################################################################
    # penalty check (step4, step5 확인)

    # penalty 1 : 싣고 있는 짐의 양 확인 --> Q = sum(De), Q - De + Re <= load_capacity
    penalty_1(neighbor, neighbor_obj, penalty, incumbent_value)
    #print("penalty_number_1 : ",penalty)

    # penalty 2 : De, Re 제약 --> load capacity 확인
    penalty_2(neighbor, neighbor_obj, penalty, incumbent_value)
    #print("penalty_2: ",penalty)




# tabu table 확인

def tabu_2(neighbor, neighbor_obj, neighbor_move, tabu_table, vehicle_route):

    # 타부이동을 한 이웃해 제거
    # 하지만, 열망수준보다 좋으면 타부이동을 해도 남김
    #print("neighbor_move: ",neighbor_move)

    for i in range(neighbor_number):
        if neighbor_obj[i] >= incumbent_value[0]:
            for k in neighbor_move[i]:
                if k in tabu_table:
                    neighbor_move[i].clear()
                    del neighbor_obj[i]
                    neighbor_obj.insert(i, 0)

    obj_count = 1000000
    for i in range(neighbor_number):
        if neighbor_obj[i] > 0:
            if obj_count > neighbor_obj[i]:
                obj_count = neighbor_obj[i].copy()
    #print("선택되는 obj : ",obj_count)
    #print("여기에 없어?: " ,neighbor_obj)

    # tabu table 갱신
    for i in range(neighbor_number):
        if obj_count == neighbor_obj[i]:
            #print("선택되는 neighbor: ",i)
            penalty2.clear()
            #print("neighbor: ",neighbor[i])
            #print("neighbor_move: ", neighbor_move[i])
            #print("penalty: ",penalty[i])
            if len(neighbor_move[i]) > 0:
                for l in range(len(neighbor_move[i])):
                    del tabu_table[0]
                for l in range(len(neighbor_move[i])):
                    tabu_table.append(neighbor_move[i][l])
            else:
                del tabu_table[0]
                del tabu_table[0]
                tabu_table.append(0)
                tabu_table.append(0)
            for j in range(len(penalty[i])):
                penalty2.append(penalty[i][j])
            for j in range(vehicle_number):
                vehicle_route[j].clear()
                for k in range(len(neighbor[i][j])):
                    vehicle_route[j].append(neighbor[i][j][k])
            break

    #print("penalty2: ",penalty2)


# 좋은 해 보관 함수
def contain(incumbent_solution, incumbent_value, candidate_solution, candidate_value, check_change):

    # 좋은해를 5개 정도 보관
    if len(candidate_value) < candidate_number:
        if incumbent_value[0] not in candidate_value:
            candidate_value.append(incumbent_value[0])
            for m in range(candidate_number):
                if len(candidate_solution[m][0]) == 0:
                    for i in range(vehicle_number):
                        for j in range(len(incumbent_solution[i])):
                            candidate_solution[m][i].append(incumbent_solution[i][j])

    elif len(candidate_value) >= candidate_number:
        if check_change != incumbent_value[0]:
            #print("안 해?")
            for m in range(candidate_number):
                if candidate_value[m] == max(candidate_value):
                    for i in range(vehicle_number):
                        candidate_solution[m][i].clear()
                        for j in range(len(incumbent_solution[i])):
                            candidate_solution[m][i].append(incumbent_solution[i][j])
                    del candidate_value[m]
                    candidate_value.insert(m, incumbent_value[0])
                    break
    #print("candidate_value: ",candidate_value)


# 초기해 보관 함수
def contain_initial(vehicle_route, vehicle_dist, X):


    for j in range(vehicle_number):
        for k in range(len(vehicle_route[j])):
            initial_solution[X][j].append(vehicle_route[j][k])
    sum = 0
    for j in range(vehicle_number):
        sum = sum + vehicle_dist[j]
    initial_value.append(sum)

"""(7) Tabu Search 알고리즘 실행"""

# 초기해 5개 생성
X = 0
while X < initial_number:

    Y = 0
    while Y < 1:

        # initial solution step 1
        initial_1(check_X, node, allocation, route_all)
        if check_X[0] == 0:
            continue

        # initial solution step 2
        initial_2(check_X, load, route_all)
        if check_X[0] == 0:
            continue

        # initial solution step 3
       # initial_3(check_X, comparison, route_all)
        #if check_X[0] == 0:
          #  continue

        # initial solution step 4
        initial_4(check_X, load, route_all)
        if check_X[0] == 0:
            continue

        Y = 1

    # 초기해 목적함수 확인
    f_route(route_all, check1, check2)
    f_dist(vehicle_route)

    # incumbent solution 확인
    incumbent(vehicle_route, vehicle_dist, incumbent_solution, incumbent_value)
    check_change = incumbent_value[0]

    # 초기해 100개 저장
    contain_initial(vehicle_route, vehicle_dist, X)

    X = X + 1
    print(X)


# 초기해 100개 중 가장 좋은 것 5개 저장
comparison.clear()
for i in range(initial_number):
    comparison.append(initial_value[i])
comparison.sort()

for i in range(candidate_number):
    # 좋은해 출처 확인
    candidate_source.append(0)

    for j in range(initial_number):
        if comparison[i] == initial_value[j]:
            candidate_value.append(initial_value[j])
            for k in range(vehicle_number):
                for l in range(len(initial_solution[j][k])):
                    candidate_solution[i][k].append(initial_solution[j][k][l])
            break

#print("초기 candidate_value: ",candidate_value)
#for i in range(candidate_number):
    #print("초기 candidate_solution: ",candidate_solution[i])


# tabu search 기반 알고리즘
# outer loop
X = 0
while X < iteration_number:

    print("vehicle_route(초기해): ",vehicle_route)

    Y = 0
    Z = 1
    while Y < inner_loop:
        print("외부루프 반복횟수: ",X+1)
        print("내부루프 반복횟수: ",Y+1)
        #print("no_bike: ", no_bike)
        #print("no_vehicle: ", no_vehicle)

        # 이웃해 생성 (2가지 방식) 및 목적함수값 확인 (penalty check 1,2)
        tabu_1(neighbor, neighbor_obj, vehicle_route)

        # 타부 목록 확인 (열망수준 넘는 것은 괜찮음) 및 갱신
        tabu_2(neighbor, neighbor_obj, neighbor_move, tabu_table, vehicle_route)

        #print("tabu_table: ",tabu_table)

        check_change = incumbent_value[0]

        # 총 이동거리 확인
        f_dist(vehicle_route)

        # 현재까지 나온 가장 좋은 해 갱신
        incumbent(vehicle_route, vehicle_dist, incumbent_solution, incumbent_value)
        #print("incumbent solution: ",incumbent_solution)
        #print("incumbent value: ",incumbent_value)
        #print("")

        # 좋은해 출처 확인
        if check_change != incumbent_value[0]:
            candidate_source.append(1)
            Z = 0


        # 좋은해를 5개 정도 보관
        contain(incumbent_solution, incumbent_value, candidate_solution, candidate_value, check_change)

        Y = Y + 1
        Z = Z + 1

    # 새로운 해 찾기

    Y = 0
    while Y < 1:

        # initial solution step 1
        initial_1(check_X, node, allocation, route_all)
        if check_X[0] == 0:
            continue

        # initial solution step 2
        initial_2(check_X, load, route_all)
        if check_X[0] == 0:
            continue

        # initial solution step 3
        initial_3(check_X, comparison, route_all)
        if check_X[0] == 0:
            continue

        # initial solution step 4
        initial_4(check_X, load, route_all)
        if check_X[0] == 0:
            continue

        Y = 1

    # 초기해 목적함수 확인
    f_route(route_all, check1, check2)
    f_dist(vehicle_route)

    check_change = incumbent_value[0]

    # incumbent solution 확인
    incumbent(vehicle_route, vehicle_dist, incumbent_solution, incumbent_value)

    # 좋은해 출처 확인
    if check_change != incumbent_value[0]:
        candidate_source.append(0)

    # 좋은해를 5개 정도 보관
    contain(incumbent_solution, incumbent_value, candidate_solution, candidate_value, check_change)


    X = X + 1



print("#############################################################")
print("")
print("optimal_solution : ", incumbent_solution)
print("optimal_value: ",incumbent_value)
print("candidate_source: ",candidate_source)
print("tabu table: ",tabu_table)
terminate_time = timeit.default_timer()
print("time : ", (terminate_time - start_time))

"""(8) 결과값 도출"""

load.clear()
for i in range(vehicle_number):
    sum_De = 0
    sum_Re = 0
    for j in range(len(incumbent_solution[i])):
        if incumbent_solution[i][j] <= N_cus:
            sum_De = sum_De + df_all['De'][incumbent_solution[i][j]-1]
            sum_Re = sum_Re + df_all['Re'][incumbent_solution[i][j]-1]
    load.append(sum_De)
print(load)

X = 0
while X < 1:
    total_dist = 0
    total_time = 0
    for i in range(vehicle_number):

            # 각 장비의 총 수요량 확인
            Q = load[i]
            dist = 0
            servicetime = 0
            deliverynumber = 0
            deliverytime = 0
            hour_time = 0
            minute_time = 0

            if vehicle_capa == 1100:
                for j in range(len(incumbent_solution[i])-1):
                    if incumbent_solution[i][j] < N_cus+1:
                        Q = Q - df_all['De'][incumbent_solution[i][j]-1] + df_all['Re'][incumbent_solution[i][j]-1]
                    elif incumbent_solution[i][j] >= N_cus+1:
                        print("Q: ",Q)

                for j in range(len(incumbent_solution[i])):
                    if j != len(incumbent_solution[i])-1:
                        dist = dist + dist_V[incumbent_solution[i][j]-1][incumbent_solution[i][j+1]-1]
                        a = a+1

                    elif j == len(incumbent_solution[i])-1 and i != vehicle_number - 1:
                        dist = dist + dist_V[incumbent_solution[i][j]-1][incumbent_solution[i+1][0]-1]
                        a = a+1
                    elif j == len(incumbent_solution[i])-1 and i == vehicle_number - 1:
                        break

                print("이동거리(km): ",dist)
                total_dist = total_dist + dist


                for j in range(len(incumbent_solution[i])-1):
                  if incumbent_solution[i][j] == N_cus+1:
                    servicetime = servicetime
                    deliverytime = deliverytime
                    deliverynumber = deliverynumber

                  else:
                    servicetime = servicetime + df_all['servicetime'][incumbent_solution[i][j]-1]
                    deliverytime = servicetime + dist/speed[i]*1000/60
                    deliverynumber = deliverynumber + df_all['Number'][incumbent_solution[i][j]-1]

                print("총시간(m): ", deliverytime)
                print("총택배개수: ", deliverynumber)
                print("")
                total_time = total_time + deliverytime
                hour_time = total_time//60
                minute_time = total_time%60


    print("")
    print("총 이동거리: ", total_dist, " km")
    print("총 배달시간: 약 ", int(hour_time), "시간 ", int(minute_time)+1, "분")


    X = 1

"""(9) 결과 시각화"""

plt.figure(figsize = (8, 8))

rr = []
lon = []
lat = []
#lon.append(127.327581)
#lat.append(37.182761)

for i in range(len(df_all['cluster'].unique())):
  for j in range(len(incumbent_solution[i])):
    rr.append(incumbent_solution[i][j])

route_all.append(rr)

for i in range(len(rr)-2):
  lon.append(df_all['longitude'][rr[i+1]-1])
  lat.append(df_all['latitude'][rr[i+1]-1])
#lon.append(127.327581)
#lat.append(37.182761)

print(len(lon))
print(lon)
print(len(lat))
print(lat)

plt.plot(lon, lat)

plt.scatter(lon, lat)

#plt.scatter(127.070490, 37.496426, marker = '*', s = 300)

plt.title('Results')
plt.xlabel('longitude', size = 12)
plt.ylabel('latitude', size = 12)
plt.show()