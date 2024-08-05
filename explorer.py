
import math
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
import time
from auxiliary import a_star,positions_possible,distance

import heapq

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

                    #input(f"{self.NAME}: type [ENTER] to proceed")


                    #o explorador terminou sua tarefa, pode recrutar um salvador
                    self.center.rescuers_count += 1
                    #enviando informação para central
                    self.center.receive_info(self.map, self.victims)

                    if self.center.is_done():
                        self.resc.go_save_victims(self.center.map, self.center.victims)
                        if self.center.kmeans_printed is False:
                            self.center.kmeans_printed = True
                            self.center.kmeans()
                        #central já processou tudo, o salvador pode ir com o mapa unificado


                    return False
                else:
                    self.explore_node(operation,wasted_time)
            else:
                return True
        ## deliberar caminho
        next_node = self.next_node()
        path,sizeGo = a_star(self,self.map,next_node,(self.x,self.y))
        _, sizeBack = a_star(self,self.map,next_node,(0,0))
        if(sizeGo+sizeBack+self.COST_READ+self.COST_DIAG*16>self.get_rtime()):
            path, sizeGo = a_star(self,self.map,(0,0),(self.x,self.y))
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
            path, dist = a_star(self,self.map,pos,cur_pos)
        
        return dist*1+origin_dist*0.3 +direction_dist*0.7




    

