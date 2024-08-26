from typing import List
from vs.abstract_agent import AbstAgent
from auxiliary import a_star,distance
from map import Map
from random import randint
GRAVITY_TO_WEIGHT = [4, 3, 2, 1] # CONST THAT HAS THE WEIGHT OF IMPORTANCE FOR EACH GRAVITY INT (BIGGER BETTER)

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
                    size = distance(posi,posf)
                    weighted_size = size/GRAVITY_TO_WEIGHT[self.victims[column][1]]
                    if(max<weighted_size):
                        max = weighted_size
                    sum+=weighted_size
                    a.append(-1)
            self.totals.append(sum)
            self.maxes.append(max)
            self.matrix.append(a)
    #-1 is the origin
    def get_cost(self, id_i,id_f):
        gravity_weight = GRAVITY_TO_WEIGHT[self.victims[id_f][1]]
        if(id_f == -1):
            gravity_weight = 1
        return self.get_distance(id_i,id_f)/gravity_weight
    
    def get_distance(self,id_i:int,id_f:int):
        if(id_i ==id_f):
            return 0
        if (self.matrix[id_i+1][id_f+1]== -1):
            return self._get_euclidian_distance(id_i,id_f)
        else:
            return self.matrix[id_i+1][id_f+1]
    
    def _get_real_distance(self,id_i:int,id_f:int):
        if(id_i ==id_f):
            return 0
        if (self.matrix[id_i+1][id_f+1] == -1):
            posi = self.all_victims[self.victims[id_i][0]][0]
            posf = self.all_victims[self.victims[id_f][0]][0]
            _, size = a_star(self.agent,self.map,posf,posi)
            weighted_size = size/GRAVITY_TO_WEIGHT[self.victims[id_f][1]]
            self.totals[id_i] = self.totals[id_i] -  distance(posi,posf)/GRAVITY_TO_WEIGHT[self.victims[id_f][1]] + weighted_size
            if(weighted_size> self.maxes[id_i]):
                self.maxes[id_i] = weighted_size
            self.matrix[id_i+1][id_f+1] = size
        return self.matrix[id_i+1][id_f+1]

    
    def _get_euclidian_distance(self,id_i,id_f):
        posi = self.all_victims[self.victims[id_i][0]][0]
        posf = self.all_victims[self.victims[id_f][0]][0]
        return distance(posi,posf)
         

    
    def get_weight(self,id:int,for_id:int):
        return self.maxes[for_id]-self.get_cost(for_id,id)

    def choose_victim(self,id:int,not_in:List[int]):
        not_sum = 0
        for i in not_in:
            not_sum += self.get_weight(i,id)
        chosen =randint(0,int(self.maxes[id]*len(self.victims) -self.totals[id]-not_sum))
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
def sequence(victims: List[tuple[int,int]],agent: AbstAgent,all_victims,map)->tuple[List[tuple[int,int]],List[int]]:
    matrix_dist = _DistanceMatrix(victims,agent,all_victims,map)
    matrix_dist.create_cost_matrix()
    all_flag = False
    count = 2*len(victims)
    path = []
    
    while(not all_flag and count>1):
        count-=1
        all_flag,path = create_path(matrix_dist,agent)
    
    parents = [path[:] for x in range(200)]
    

    for i in range(100):
        parents = generation(matrix_dist,agent,parents)

    max = 0
    id = 0
    parents.sort(key= lambda p: evaluate(p,matrix_dist))
    path = parents[0][:]
    
    real_path = []
    id_path = []
    for i in path:
        real_path.append(all_victims[victims[i][0]][0])
        id_path.append(victims[i][0])
    
    return real_path, id_path

def evaluate(path,matrix_dist:_DistanceMatrix)->int:
    sum:int = 0
    for victim in path:
        id, grav = matrix_dist.victims[victim]
        sum+= GRAVITY_TO_WEIGHT[grav]
    return sum

def is_valid(path:List[int],matrix_dist:_DistanceMatrix):
    path_copy = path[:]
    while(path):
        victim = path_copy.pop()
        if victim in path:
            return False
    return True

#ox_crossover
def procreate(father:List[int],mother:List[int],matrix_dist:_DistanceMatrix):
    father_main = randint(0,1)
    main_parent = mother
    other_parent = father
    if(father_main):
        main_parent = father
        other_parent = mother

    cut = randint(0,len(main_parent)-1)
    child = main_parent[:cut]
    for victim in other_parent:
        if(victim not in child):
            child.append(victim)
    return child
    

def mutate_path(path:List[int],matrix_dist:_DistanceMatrix,chance:float):
    for victim in path:
        mutation_possibility = randint(0,10000)/10000
        if(mutation_possibility<=chance):
            change_with = randint(0,len(matrix_dist.victims)-1)
            if(change_with in path):
                index =path.index(change_with)
                aux = victim
                path[path.index(victim)] = change_with
                path[index] = aux
            else:
                path[path.index(victim)] = change_with
    return path

def generation(matrix_dist:_DistanceMatrix,agent:AbstAgent,children:List[List[int]]):
    roleta = []
    sum = 0
    for child in children:
        if(possible(child.copy(),matrix_dist,agent)):
            sum+= evaluate(child,matrix_dist)
        else:
            sum+=1
        roleta.append(sum)
    
    parents = []
    for i in range(len(children)*2):
        random = randint(0, roleta[-1])
        for bucket in roleta:
            
            
            if random <= bucket:
                parents.append(children[roleta.index(bucket)].copy())
                break
    new_children = []
    for i in range(0,len(parents),2):
        new_child = procreate(parents[i],parents[i+1],matrix_dist)
        new_child = mutate_path(new_child,matrix_dist,0.005)
        new_c = new_child[:]
        if(possible(new_child,matrix_dist,agent)):
            new_children.append(new_c)
        else:
            new_children.append(parents[i])
    return new_children
            
        




def create_path(matrix_dist:_DistanceMatrix,agent:AbstAgent):
    life = agent.TLIM
    path = []
    last = -1
    all_flag = False
    while(life>matrix_dist.get_distance(last,-1)):
        next_victim = matrix_dist.choose_victim_minimum(last,path)
        path.append(next_victim)
        if(next_victim==-1):
            all_flag = True
            break
        life-= matrix_dist._get_real_distance(last,next_victim)
        life-= agent.COST_FIRST_AID
        
        last = next_victim

    if(path):
        path.pop()
    
    return all_flag, path

def possible(path,matrix_dist:_DistanceMatrix,agent:AbstAgent):
    life = agent.TLIM
    last = -1
    all_flag = False
    while(path):
        next_victim = path.pop()
        life-= matrix_dist._get_real_distance(last,next_victim)
        life-= agent.COST_FIRST_AID
        last = next_victim
    
    return life>0