#Classe que recupera as informações dos exploradores, trata e devolve aos salvadores já processado
from map import Map, mix_maps
import random
import matplotlib.pyplot as plt
import os
import shutil
from rescuer import Rescuer
from sequencing import sequence
#possui um mapa de informações que é atualizado a cada passo
#possui uma função para receber as informações dos exploradores

class Center:
    def __init__(self):
        self.map = Map()
        self.victims = {}
        self.rescuers = []
        self.explorers_count = 0
        self.kmeans_printed = False
        self.path = ""

    def receive_info(self, exp_map: Map, victims: dict):
        self.map = mix_maps(self.map, exp_map)
        self.add_victims(victims)
        self.explorers_count-=1
        print("Center received info from an explorer")
        if self._is_done():
                if self.kmeans_printed is False:
                    self.kmeans_printed = True
                    groups =self.kmeans()
                    paths = []
                    for group in groups:
                        rescuer:Rescuer = self.rescuers.pop()
                        path,path_id = sequence(self.find_gravity(group),rescuer,self.victims,self.map)
                        paths.append(path_id)
                        print(path)
                        rescuer.go_save_victims(self.map,path)
                    for i in range(len(paths)):
                        self.save_seq(paths[i],i)

    def add_rescuer(self,resc:Rescuer):
        if resc not in self.rescuers:
            self.rescuers.append(resc)
        


    def find_gravity(self,group):
        gravity_group = []
        for victim in group:
            gravity_group.append((victim,0)) #set all to gravity 0
        return gravity_group



            

    def _is_done(self):
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
        plt.yticks(range(min_y, max_y + 1))  # Ajustado para os valores de y corretos

        # Adiciona a grade
        plt.grid(True)

        # Títulos dos eixos e do gráfico
        plt.xlabel("Pos x")
        plt.ylabel("Pos y")
        plt.title('Clusters')
        
        
        # Inverte o eixo y
        plt.gca().invert_yaxis()
        try:
            plt.savefig(f"clusters_{self.path}/clusters.png")  # dpi ajustado para uma imagem 1920x1080
        except OSError as error:
            print(error)

        #plt.show()  # Mostra o gráfico


    
    def get_centroids(self):
        k = len(self.rescuers)
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
        try:
            os.mkdir(f'clusters_{self.path}')
        except OSError as _:
            if os.path.exists(f'clusters_{self.path}'):
                shutil.rmtree(f'clusters_{self.path}')
                os.mkdir(f'clusters_{self.path}')
        for i in range(len(groups)):

            with open(f'clusters_{self.path}/cluster{i+1}.txt', 'w') as f:
                f.write('id, x, y, grav, label\n')
                #ordenando groups pelo id da vítima
                groups[i].sort()             
                for j in range(len(groups[i])):
                        x = self.victims[groups[i][j]][0][0]
                        y = self.victims[groups[i][j]][0][1]
                        id = groups[i][j]
                        score = vitals_signals_mapped[id][0]
                        label = vitals_signals_mapped[id][1]
                        f.write(f'{id}, {x}, {y}, {score}, {label}\n')

    def save_seq(self, id_path,g_n):
    #saving the groups in format 𝑖𝑑, 𝑥, 𝑦, gravidade, label de criticidade
        vitals_signals_mapped = self.mapping_vital_signals()
        try:
            os.mkdir(f'seqs_{self.path}')
        except OSError as _:
            if os.path.exists(f'seqs_{self.path}'):
                shutil.rmtree(f'seqs_{self.path}')
                os.mkdir(f'seqs_{self.path}')
        with open(f'seqs_{self.path}/seq{g_n+1}.txt', 'w') as f:
            f.write('id, x, y, grav, label\n')
            #ordenando groups pelo id da vítima           
            for j in range(len(id_path)):
                    id = id_path[j]
                    x = self.victims[id][0][0]
                    y = self.victims[id][0][1]
                    
                    score = vitals_signals_mapped[id][0]
                    label = vitals_signals_mapped[id][1]
                    f.write(f'{id}, {x}, {y}, {score}, {label}\n')
            f.close()
                

                
    def kmeans(self):
        
        centroids = self.get_centroids()
        if centroids is None:
            print("No centroids found")
            return []
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
        return groups
        

        