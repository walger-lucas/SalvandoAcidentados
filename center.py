#Classe que recupera as informações dos exploradores, trata e devolve aos salvadores já processado
from map import Map, mix_maps

#possui um mapa de informações que é atualizado a cada passo
#possui uma função para receber as informações dos exploradores
class Center:
    def __init__(self):
        self.map = Map()
        self.victims = {}
        self.nb_victims = 0
        self.rescuers_count = 0
        self.rescuers_slices = 0
        self.explorers_count = 0

    def receive_info(self, exp_map: Map, victims: dict):
        self.map = mix_maps(self.map, exp_map)
        self.add_victims(victims)
        self.explorers_count -= 1
        print("Center received info from an explorer")

    def is_done(self):
        if self.explorers_count == 0:
            print("\n\nCenter is done\n\n")
            return True
    def add_victims(self, victims):
        #victims : seq -> (x,y) , <vs>
        for victim in victims:
            #vendo se a coordenada já está no dicionario de vitimas, se sim ignora
            if victims[victim][0] not in self.victims.values():
                self.nb_victims += 1
                self.victims[self.nb_victims] = victims[victim]

            