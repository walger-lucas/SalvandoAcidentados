##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim
### Not a complete version of DFS; it comes back prematuraly
### to the base when it enters into a dead end position


import os
import random
from typing import List
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod
from auxiliary import a_star


## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map:Map            # explorer will pass the map
        self.victims = []         # list of found victims
        self.plan_x = 0             # the x position of the rescuer during the planning phase
        self.plan_y = 0             # the y position of the rescuer during the planning phase
        self.plan_visited = set()   # positions already planned to be visited 
        self.plan_rtime = self.TLIM # the remaing time during the planning phase
        self.plan_walk_time = 0.0   # previewed time to walk during rescue
        self.x = 0                  # the current x position of the rescuer when executing the plan
        self.y = 0                  # the current y position of the rescuer when executing the plan
        self.walk_vec = []
        self.come_back = False
                
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

    
    def go_save_victims(self, map:Map, victims:List[tuple[int,int]]):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""

        #print(f"\n\n*** R E S C U E R ***")
        self.map = map
        #print(f"{self.NAME} Map received from the explorer")
        #self.map.draw()

        #print()
        #print(f"{self.NAME} List of found victims received from the explorer")
        self.victims = victims
        victims.reverse()

        # print the found victims - you may comment out
        #for seq, data in self.victims.items():
        #    coord, vital_signals = data
        #    x, y = coord
        #    print(f"{self.NAME} Victim seq number: {seq} at ({x}, {y}) vs: {vital_signals}")

        #print(f"{self.NAME} time limit to rescue {self.plan_rtime}")                  
        self.set_state(VS.ACTIVE)
        
        
    def deliberate(self) -> bool:
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
            if self.walk_vec==[]:
                ##came back to start
                if(self.x==0 and self.y==0):
                    print(f"{self.NAME}: rtime {self.get_rtime()}")
                    return False
                else:
                    self.first_aid()
            else:
                return True
        if(self.x==0 and self.y==0 and self.come_back ==True):
            print(f"{self.NAME}: rtime {self.get_rtime()}")

            return False
        path = []
        ## deliberar caminho
        if(self.victims==[]):
            path, sizeGo = a_star(self,self.map,(0,0),(self.x,self.y))
            self.come_back = True
        else:
            next_node = self.victims.pop()
            print(next_node)
            path,sizeGo = a_star(self,self.map,next_node,(self.x,self.y))
            _, sizeBack = a_star(self,self.map,next_node,(0,0))

        self.walk_vec = path
        return True

