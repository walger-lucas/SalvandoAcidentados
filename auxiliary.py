import heapq
import math;
from map import Map;
from vs.abstract_agent import AbstAgent
from vs.constants import VS

def positions_possible(current,actions_res):
    i = 0
    actions = []
    while i<8:
        if actions_res[i] == VS.CLEAR:
            actions.append((current[0] + AbstAgent.AC_INCR[i][0],current[1] + AbstAgent.AC_INCR[i][1]))
        i+=1
    return actions

def distance(p1,p2):
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    return math.sqrt(dx*dx+dy*dy)

def a_star(agent:AbstAgent,map:Map, posf,posi):
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
            for p in positions_possible(cur_node,map.get(cur_node)[2]):
                weight = agent.COST_LINE
                dp = (p[0]-cur_node[0],p[1]-cur_node[1])
                if(dp[0]!=0 and dp[1]!=0):
                    weight = agent.COST_DIAG
                ## only allow access through known map
                ground = 1.0
                if map.in_map(p):
                    ground = map.get(p)[0]
                elif p != posf:
                    continue

                temp_g = g_score[cur_node] + weight*ground
                if(p not in g_score.keys() or g_score[p]> temp_g ):
                    g_score[p] = temp_g
                    f_score[p] = g_score[p]+distance(p,posf)
                    last_node[p] = cur_node
                    heapq.heappush(queue,(f_score[p],p))
        cur_pos = posf
        sum = 0
        next_pos = last_node[cur_pos]
        path.append((cur_pos[0]-next_pos[0],cur_pos[1]-next_pos[1]))
        if(map.in_map(posf)):
            if((cur_pos[0]==next_pos[0] or cur_pos[1]==next_pos[1])):
                sum+= map.get(cur_pos)[0]*agent.COST_LINE
            else:
                sum+= map.get(cur_pos)[0]*agent.COST_DIAG
        cur_pos = next_pos
        while cur_pos != posi:
            next_pos = last_node[cur_pos]
            path.append((cur_pos[0]-next_pos[0],cur_pos[1]-next_pos[1])) ## sets direction
            if((cur_pos[0]==next_pos[0] or cur_pos[1]==next_pos[1])):
                sum+= map.get(cur_pos)[0]*agent.COST_LINE
            else:
                sum+= map.get(cur_pos)[0]*agent.COST_DIAG
            cur_pos = next_pos
        #path is inverted
        return path, sum