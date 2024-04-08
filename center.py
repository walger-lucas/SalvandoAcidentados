#Classe que recupera as informações dos exploradores, trata e devolve aos salvadores já processado
from map import Map, mix_maps
import random
import matplotlib.pyplot as plt

#possui um mapa de informações que é atualizado a cada passo
#possui uma função para receber as informações dos exploradores
class Center:
    def __init__(self):
        self.map = Map()
        self.victims = {}
        self.rescuers_count = 0
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
        else:
            return False

    def get_min_max_x_y(self):
        if self.map is None or self.map.map_data == {}:
            return None, None, None, None
        min_x = min(key[0] for key in self.map.map_data.keys())
        max_x = max(key[0] for key in self.map.map_data.keys())
        min_y = min(key[1] for key in self.map.map_data.keys())
        max_y = max(key[1] for key in self.map.map_data.keys())
        return min_x, max_x, min_y, max_y
    

    def add_victims(self, victims):
        for victim in victims: 
            # Verifica se a vítima já existe
            if victim not in self.victims.keys():
                self.victims[victim] = victims[victim]
        self.victims = dict(sorted(self.victims.items()))



    def plot_clusters(self, centroids, groups):
        # Plota pontos dos grupos
        plt.figure(figsize=(19.20, 10.80), dpi=100)
        for j in range(len(groups)):
            for i in range(len(groups[j])):
                plt.scatter(self.victims[groups[j][i]][0][0], self.victims[groups[j][i]][0][1], color=centroids[j][2])

        # Plota centroides
        for i, centroid in enumerate(centroids):
            plt.scatter(centroid[0], centroid[1], color=centroid[2])
            plt.text(centroid[0], centroid[1], f'C{i+1}')

        # Marca o ponto (0, 0)
        plt.axvline(x=0, color='k', linestyle='--', linewidth=1)  # Linha vertical
        plt.axhline(y=0, color='k', linestyle='--', linewidth=1)  # Linha horizontal
        
        min_x, max_x, min_y, max_y = self.get_min_max_x_y()
        if min_x is None or max_x is None or min_y is None or max_y is None:
            return
        
        # Define os intervalos dos ticks nos eixos x e y para cada unidade

        plt.xticks(range(min_x, max_x))
        plt.yticks(range(-max_y, -min_y))

        # Adiciona a grade
        plt.grid(True)

        # Títulos dos eixos e do gráfico
        plt.xlabel("Pos x")
        plt.ylabel("Pos y")
        plt.title('Clusters')
        plt.savefig("clusters.png")  # dpi ajustado para uma imagem 1920x1080
        #plt.show()  # Mostra o gráfico

    
    def get_centroids(self):
        k = self.rescuers_count
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        poskx = []
        posky = []
        centroids = []
        
        min_x, max_x, min_y, max_y = self.get_min_max_x_y()
        if min_x is None or max_x is None or min_y is None or max_y is None:
            return None
        for i in range(k):
            poskx.append(random.randint(min_x,max_x))
            posky.append(random.randint(min_y,max_y))
            color = colors[i]

            centroids.append((poskx[i],posky[i], color))
        return centroids
    
    def update_centroids(self, centroids, groups):
    
        for i in range(len(centroids)):
            if len(groups[i]) == 0:
                continue
            x = 0
            y = 0
            for j in range(len(groups[i])):
                x += self.victims[groups[i][j]][0][0]
                y += self.victims[groups[i][j]][0][1]

            x = x/len(groups[i])
            y = y/len(groups[i])
            centroids[i] = (x, y, centroids[i][2])
        return centroids
    

    def update_groups(self, centroids):
        groups = []
    
        for i in range(len(centroids)):
            groups.append([])

        for victim in self.victims:
            min_dist = 99999
            group = -1
            for centroid in range(len(centroids)):
               
                dist = ((self.victims[victim][0][0] - centroids[centroid][0])**2 + (self.victims[victim][0][1] - centroids[centroid][1])**2)**0.5

                if dist < min_dist:
                    min_dist = dist
                    group = centroid

            groups[group].append(victim)
        return groups
    
    def get_max_diff_dist_victims(self, groups):
        
        dist_victims = []
        for k in range(len(groups)):
            dist_victims.append(0)
            for i in range(len(groups[k])):
                for j in range(i+1, len(groups[k])):
                    dist_victims[k] += ((self.victims[groups[k][i]][0][0] - self.victims[groups[k][j]][0][0])**2 + (self.victims[groups[k][i]][0][1] - self.victims[groups[k][j]][0][1])**2)**0.5
        total_dist = 0

        for i in range(len(dist_victims)):
            total_dist += dist_victims[i]
        return total_dist, max(dist_victims)-min(dist_victims)
    
    def mapping_vital_signals(self):
        vital_signals_mapped = {}
        for k in self.victims:
            vital_signals = self.victims[k][1]
            #𝑝𝐷𝑖𝑎𝑠𝑡, 𝑝𝑆𝑖𝑠𝑡, 𝑞𝑃𝐴, 𝑝𝑢𝑙𝑠𝑜, 𝑓𝑅𝑒𝑠
            #𝑝𝐷𝑖𝑎𝑠𝑡: pressão diastólica
            #𝑝𝑆𝑖𝑠𝑡: pressão sistólica
            #𝑞𝑃𝐴: quantidade de sangue que passa por uma área em um determinado tempo
            #𝑝𝑢𝑙𝑠𝑜: pulso
            #𝑓𝑅𝑒𝑠: frequência respiratória
            #making the mapping of the vital signals to a scale of 0 to 100 0 is the worst and 100 is the best
            vital_signals_value = 0

            #pressão diastólica
            if vital_signals[1] < 60:
                vital_signals_value += 0
            elif vital_signals[1] < 80:
                vital_signals_value += 25
            elif vital_signals[1] < 90:
                vital_signals_value += 50
            elif vital_signals[1] < 100:
                vital_signals_value += 75
            else:
                vital_signals_value += 100

            #pressão sistólica
            if vital_signals[2] < 90:
                vital_signals_value += 0
            elif vital_signals[2] < 120:
                vital_signals_value += 25
            elif vital_signals[2] < 130:
                vital_signals_value += 50
            elif vital_signals[2] < 140:
                vital_signals_value += 75
            else:
                vital_signals_value += 100

            #quantidade de sangue que passa por uma área em um determinado tempo
            if vital_signals[3] < 4:
                vital_signals_value += 0
            elif vital_signals[3] < 5:
                vital_signals_value += 25
            elif vital_signals[3] < 6:
                vital_signals_value += 50
            elif vital_signals[3] < 7:
                vital_signals_value += 75
            else:
                vital_signals_value += 100

            #pulso
            if vital_signals[4] < 50:
                vital_signals_value += 25
            elif vital_signals[4] < 60:
                vital_signals_value += 0
            elif vital_signals[4] < 100:
                vital_signals_value += 50
            elif vital_signals[4] < 120:
                vital_signals_value += 75
            else:
                vital_signals_value += 100

            #frequência respiratória
            if vital_signals[5] < 12:
                vital_signals_value += 100
            elif vital_signals[5] < 16:
                vital_signals_value += 75
            elif vital_signals[5] < 20:
                vital_signals_value += 50
            elif vital_signals[5] < 24:
                vital_signals_value += 25
            else:
                vital_signals_value += 0

            
            if vital_signals_value/5 <=25:
                vital_signals_mapped[k] = (vital_signals_value/5, 4)
            elif vital_signals_value/5 <=50:
                vital_signals_mapped[k] = (vital_signals_value/5, 3)
            elif vital_signals_value/5 <=75:
                vital_signals_mapped[k] = (vital_signals_value/5, 2)
            else:
                vital_signals_mapped[k] = (vital_signals_value/5, 1)
        return vital_signals_mapped 


    def save_groups(self, groups):
    #saving the groups in format 𝑖𝑑, 𝑥, 𝑦, gravidade, label de criticidade
        vitals_signals_mapped = self.mapping_vital_signals()
        with open('groups.csv', 'w') as f:
            for i in range(len(groups)):
                #ordenando groups pelo id da vítima
                groups[i].sort()             
                f.write(f'Group {i+1}\n')
                for j in range(len(groups[i])):
                        x = self.victims[groups[i][j]][0][0]
                        y = self.victims[groups[i][j]][0][1]
                        id = groups[i][j]
                        score = vitals_signals_mapped[id][0]
                        label = vitals_signals_mapped[id][1]
                        f.write(f'{id}, {x}, {y}, {score}, {label}\n')
                

                
    def kmeans(self):
        
        centroids = self.get_centroids()
        if centroids is None:
            print("No centroids found")
            return
        groups = []
        for i in range(len(centroids)):
            groups.append([])
        old_centroids = []

        groups = self.update_groups(centroids)
        centroids = self.update_centroids(centroids, groups)
        while(centroids != old_centroids):
            old_centroids = centroids
            groups = self.update_groups(centroids)
            centroids = self.update_centroids(centroids, groups)

        total, diff_dist_victims = self.get_max_diff_dist_victims(groups)
        while(diff_dist_victims > total/len(groups)/len(groups)):
            centroids = self.get_centroids()
            old_centroids = []
            while(centroids != old_centroids):
                old_centroids = centroids
                groups = self.update_groups(centroids)
                centroids = self.update_centroids(centroids, groups)
            total, diff_dist_victims = self.get_max_diff_dist_victims(groups)

        self.save_groups(groups)
        self.plot_clusters(centroids, groups)
        

        