#Classe que recupera as informações dos exploradores, trata e devolve aos salvadores já processado
from map import Map, mix_maps
import random
import matplotlib.pyplot as plt
from vs.constants import VS

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
        self.kmeans_printed = False

    def receive_info(self, exp_map: Map, victims: dict):
        self.map = mix_maps(self.map, exp_map)
        self.add_victims(victims)
        self.explorers_count -= 1
        print("Center received info from an explorer")

    def is_done(self):
        if self.explorers_count == 0:
            print("\n\nCenter is done\n\n")
            if self.map is None or self.map.map_data == {}:
                print("Center map is empty.")
                return False
            else:
                return True


    def add_victims(self, victims):
        #victims : seq -> (x,y) , <vs>
        for victim in victims:
            #vendo se a coordenada já está no dicionario de vitimas, se sim ignora
            if victims[victim][0] not in self.victims.values():
                self.nb_victims += 1
                self.victims[self.nb_victims] = victims[victim]



    def plot_clusters(self, centroids):
        if self.map is None or self.map.map_data == {} or self.victims == 0:
            return
        min_x = min(key[0] for key in self.map.map_data.keys())
        max_x = max(key[0] for key in self.map.map_data.keys())
        min_y = min(key[1] for key in self.map.map_data.keys())
        max_y = max(key[1] for key in self.map.map_data.keys())

        victims_pos_x = []
        victims_pos_y = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                item = self.map.get((x, y))
                if item:
                    if item[1] != VS.NO_VICTIM:
                        victims_pos_x.append(x)
                        victims_pos_y.append(-y)
        color = (random.uniform(0, 1),random.uniform(0, 1),random.uniform(0, 1),1)
        for i in range(len(victims_pos_x)):
            plt.scatter(victims_pos_x[i], victims_pos_y[i], color=color)

        # Plota centroides
        for i, centroid in enumerate(centroids):
            plt.scatter(centroid[0], centroid[1], color=centroid[2])
            plt.text(centroid[0], centroid[1], f'C{i+1}')

        # Títulos dos eixos e do gráfico
        plt.xlabel("Pos x")
        plt.ylabel("Pos y")
        plt.title('Clusters')
        plt.show()  # Show the plot

    def kmeans(self):
        k = self.rescuers_count
        poskx = []
        posky = []
        centroids = []
        if self.map is None or self.map.map_data == {} or self.victims == 0:
            return
        min_x = min(key[0] for key in self.map.map_data.keys())
        max_x = max(key[0] for key in self.map.map_data.keys())
        min_y = min(key[1] for key in self.map.map_data.keys())
        max_y = max(key[1] for key in self.map.map_data.keys())
        for i in range(k):
            poskx.append(random.randint(min_x,max_x))
            posky.append(random.randint(min_y,max_y))
            color = (random.uniform(0.5, 1),random.uniform(0.5, 1),random.uniform(0.5, 1),1)
            centroids.append((poskx[i],posky[i], color))
        self.plot_clusters(centroids)
        