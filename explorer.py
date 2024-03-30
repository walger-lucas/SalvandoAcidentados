import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
import time
import center

import heapq

def positions_possible(current,actions_res):
    i = 0
    actions = []
    while i<8:
        if actions_res[i] == VS.CLEAR:
            actions.append((current[0] + Explorer.AC_INCR[i][0],current[1] + Explorer.AC_INCR[i][1]))
        i+=1
    return actions
    

class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc,id,total_ag, center):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.center = center
        center.explorers_count += 1
        self.walk_vec = []
        self.to_explore = []
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.angle = math.pi*2/total_ag
        self.id = id
        self.direction = (math.cos(self.angle*id),math.sin(self.angle*id)) #direction where it will try to go
        self.distance = math.sqrt(self.TLIM)*2/self.COST_LINE

        actions_res = self.check_walls_and_lim()
        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, actions_res)
        for pos in positions_possible((self.x,self.y),actions_res):
            if not self.map.in_map(pos):
                self.to_explore.append(pos)
        
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        #stime.sleep(0.1)
        if self.walk_vec:
            ## continue path
            wasted_time = self.get_rtime()
            operation = self.walk_vec.pop()
            self.walk(operation[0], operation[1])
            self.x += operation[0]
            self.y += operation[1]
            wasted_time -= self.get_rtime() 
            ## path ended
            if self.walk_vec == []:
                ##came back to start
                if(self.x==0 and self.y==0):
                    print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
                    print("\n\n\n\nMAPA:")
                    self.map.draw()
                    #input(f"{self.NAME}: type [ENTER] to proceed")
                    self.center.rescuers_count += 1
                    self.center.receive_info(self.map, self.victims)

                    if self.center.is_done():


                        self.resc.go_save_victims(self.center.map, self.center.victims)
                    return False
                else:
                    self.explore_node(operation,wasted_time)
            else:
                return True
        ## deliberar caminho
        next_node = self.next_node()
        path,sizeGo = self.a_star(next_node,(self.x,self.y))
        path2, sizeBack = self.a_star(next_node,(0,0))
        if(sizeGo+sizeBack+self.COST_READ+self.COST_DIAG*16>self.get_rtime()):
            path, sizeGo = self.a_star((0,0),(self.x,self.y))
        self.walk_vec = path
        return True

    
    def next_node(self) -> tuple[int,int]:
        if self.to_explore:
            min = (self.heuristica(self.to_explore[0]),self.to_explore[0])
            for pos in self.to_explore[1:]:
                heuristica = self.heuristica(pos)
                if min[0] > heuristica:
                    min = (heuristica,pos)
            
            self.to_explore.remove(min[1])

            return min[1]
        else:
            return (0,0)
    

    
    def a_star(self, posf,posi):
        path = []
        last_node = {}
        g_score = {}
        f_score = {}
        g_score[posi]=0
        f_score[posi]= distance(posf,posi)
        queue = [(0,posi)] #heap disfarcado
        while queue:
            cur_f, cur_node = heapq.heappop(queue)
            if cur_node == posf:
                break
            for p in positions_possible(cur_node,self.map.get(cur_node)[2]):
                weight = self.COST_LINE
                dp = (p[0]-cur_node[0],p[1]-cur_node[1])
                if(dp[0]!=0 and dp[1]!=0):
                    weight = self.COST_DIAG
                ## only allow access through known map
                ground = 1.0
                if self.map.in_map(p):
                    ground = self.map.get(p)[0]
                elif p != posf:
                    continue

                temp_g = g_score[cur_node] + weight*ground
                if(p not in g_score.keys() or g_score[p]> temp_g ):
                    g_score[p] = temp_g
                    f_score[p] = g_score[p]+distance(p,posf)
                    last_node[p] = cur_node
                    heapq.heappush(queue,(f_score[p],p))
        cur_pos = posf
        while cur_pos != posi:
            next_pos = last_node[cur_pos]
            path.append((cur_pos[0]-next_pos[0],cur_pos[1]-next_pos[1])) ## sets direction
            cur_pos = next_pos
        #path is inverted
        return path, f_score[posf]


    def explore_node(self,operation,wasted_time):
        cost = wasted_time/self.COST_LINE
        if operation[0] !=0 and operation[1]!=1:
            cost = wasted_time/self.COST_DIAG

        seq = self.check_for_victim()
        if seq != VS.NO_VICTIM:
            vs = self.read_vital_signals()
            self.victims[vs[0]] = ((self.x, self.y), vs)

        actions_res = self.check_walls_and_lim()
        self.map.add((self.x, self.y), cost, seq, actions_res)
        for pos in positions_possible((self.x,self.y),actions_res):
            if not self.map.in_map(pos) and not pos in self.to_explore:
                self.to_explore.append(pos)
        
    def heuristica(self,pos):
        cur_pos = (self.x,self.y)
        #calculo de modificador da distância objetivo a procurar em função da porcentagem de bateria atual
        mod = max(self.get_rtime()/self.TLIM,0)
        mod = pow(mod,1.2)+ 0.1
        proj_ort_dist = pos[0]*self.direction[0] + pos[1]*self.direction[1]##calcula o modulo da projecao ortogonal do vetor da posicao atual e da direcao preferida
        length = self.distance*mod
        #modificador de direção, o quao mais pra sua direção, mais negativo
        direction_dist = abs(proj_ort_dist-length)
        radius = distance(pos,(0,0))
        origin_dist= abs(radius-length)
        dist = distance(pos,cur_pos)
        # caso a distancia atual do ponto seja menor que 10, descubra a distância real
        if(dist<10):
            path, dist = self.a_star(pos,cur_pos)
        
        return dist*1+origin_dist*0.3 +direction_dist*0.7
        
def distance(p1,p2):
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    return math.sqrt(dx*dx+dy*dy)




    

