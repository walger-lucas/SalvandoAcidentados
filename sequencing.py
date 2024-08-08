from typing import List
from vs.abstract_agent import AbstAgent
from auxiliary import a_star
from map import Map
from random import randint
GRAVITY_TO_WEIGHT = [1,2,3,4] # CONST THAT HAS THE WEIGHT OF IMPORTANCE FOR EACH GRAVITY INT (BIGGER BETTER)

class _DistanceMatrix:
    def __init__(self,victims: List[tuple[int,int]],agent: AbstAgent,all_victims,map):
        self.victims = victims.copy()
        self.agent = agent
        self.all_victims = all_victims
        self.map = map
        pass
    def create_cost_matrix(self):
        self.matrix = []
        self.totals = []
        self.maxes = []
    
        a = [0.0]
        for column in range(len(self.victims)):
            posf = self.all_victims[self.victims[column][0]][0] #first info of self.victims is id and first info of center.victims is position
            _, size = a_star(self.agent,self.map,posf,(0,0))
            a.append(size)
        self.matrix.append(a)
        
        for row in range(len(self.victims)):
            a = []
            posi = self.all_victims[self.victims[row][0]][0]
            _,size = a_star(self.agent,self.map,(0,0),posi)
            a.append(size)
            max = 0
            sum = 0
            for column in range(len(self.victims)):
                if(column == row):
                    a.append(0.0)
                else:
                    posf = self.all_victims[self.victims[column][0]][0] #first info of self.victims is id and first info of center.victims is position
                    _, size = a_star(self.agent,self.map,posf,posi)
                    weighted_size = size/GRAVITY_TO_WEIGHT[self.victims[column][1]]
                    if(max<weighted_size):
                        max = weighted_size
                    sum+=weighted_size
                    a.append(size)
            self.totals.append(sum)
            self.maxes.append(max)
            self.matrix.append(a)
    #-1 is the origin
    def get_cost(self, id_i,id_f):
        gravity_weight = GRAVITY_TO_WEIGHT[self.victims[id_f][1]]
        if(id_f == -1):
            gravity_weight = 1
        return self.matrix[id_i+1][id_f+1]/gravity_weight
    
    def get_distance(self,id_i:int,id_f:int):
        if(id_i ==id_f):
            return 0
        return self.matrix[id_i+1][id_f+1]
    
    def get_weight(self,id:int,for_id:int):
        return self.maxes[for_id]-self.get_cost(for_id,id)

    def choose_victim(self,id:int,not_in:List[int]):
        not_sum = 0
        for i in not_in:
            not_sum += self.get_weight(i,id)
        chosen =randint(0,self.maxes[id]*len(self.victims) -self.totals[id]-not_sum)
        id_next = -1
        while(chosen>0):
            id_next+=1
            if(id_next not in not_in):
                chosen-= self.get_weight(id_next,id)
        return id_next
        
    def choose_victim_minimum(self,id:int, not_in:List[int]):
        min = -1
        cost = 80000000
        
        for i in range(0,len(self.victims)):
            if(i not in not_in and id!=i):
                if self.get_cost(id,i)<cost:
                    min = i
                    cost = self.get_cost(id,i)
        return min


        

        
    






#receives list of tuples (id, gravity_code)
def sequence(victims: List[tuple[int,int]],agent: AbstAgent,all_victims,map)->List[tuple[int,int]]:
    matrix_dist = _DistanceMatrix(victims,agent,all_victims,map)
    matrix_dist.create_cost_matrix()
    life = agent.TLIM
    path = []
    last = -1
    all_flag = False
    while(life>matrix_dist.get_distance(last,-1)):
        next_victim = matrix_dist.choose_victim_minimum(last,path)
        life-= matrix_dist.get_distance(last,next_victim)
        life-= agent.COST_FIRST_AID
        path.append(next_victim)
        last = next_victim
        if(next_victim==-1):
            break
    if(path):
        path.pop()
    real_path = []
    for i in path:
        real_path.append(all_victims[victims[i][0]][0])
    return real_path

