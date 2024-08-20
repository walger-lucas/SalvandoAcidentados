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





import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

class Center:
    def __init__(self):
        self.map = Map()
        self.victims = {}
        self.victim_id_gravityValue_gravityClass = {}
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
                        #print(path)
                        self.save_group(group, groups.index(group)+1)
                        rescuer.go_save_victims(self.map,path)
                    for i in range(len(paths)):

                        self.save_seq(paths[i],i)

    def add_rescuer(self,resc:Rescuer):
        if resc not in self.rescuers:
            self.rescuers.append(resc)
        


    def find_gravity(self,group):
        gravity_group = []
        model = load_model('classifier_models/model_2.h5')


        for victim in group:
            #victim: ((x,y), <seq, pSist, pDiast, qPA, pulse, respiratory freq>)
            #usign qPA, pulse and respiratory freq to calculate the gravity class using Classifier
            #print(f"Victim {victim}: {self.victims[victim]}")


            features = [self.victims[victim][1][3], self.victims[victim][1][4], self.victims[victim][1][5]]
            features = np.array(features).reshape(1,3)
            prediction = model.predict(features, verbose=0)
            gravity_group.append((victim,np.argmax(prediction)))
            self.victim_id_gravityValue_gravityClass[victim] = {"gravityValue":np.max(prediction), "gravityClass":np.argmax(prediction)}

            # self.victim_id_gravityValue_gravityClass.append((victim,0,0))
            # gravity_group.append((victim,0))
        print(f"Gravity group: {gravity_group}")
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
    
   

    def save_group(self, group, n):
    #saving the groups in format 𝑖𝑑, 𝑥, 𝑦, gravidade, label de criticidade
        try:
            os.mkdir(f'clusters_{self.path}')
        except OSError as _:
            if os.path.exists(f'clusters_{self.path}'):
                print("Directory exists")
        with open(f'clusters_{self.path}/cluster{n}.txt', 'w') as f:
            f.write('id, x, y, grav, label\n')
            #ordenando groups pelo id da vítima
            group.sort()             
            for j in range(len(group)):
                    x = self.victims[group[j]][0][0]
                    y = self.victims[group[j]][0][1]
                    id = group[j]
                    score = self.victim_id_gravityValue_gravityClass[id]["gravityValue"]*100
                    label = self.victim_id_gravityValue_gravityClass[id]["gravityClass"] + 1
                    f.write(f'{id}, {x}, {y}, {score}, {label}\n')

    def save_seq(self, id_path,g_n):
    #saving the groups in format 𝑖𝑑, 𝑥, 𝑦, gravidade, label de criticidade
        try:
            os.mkdir(f'seqs_{self.path}')
        except OSError as _:
            if os.path.exists(f'seqs_{self.path}'):
                print("Directory exists")
        with open(f'seqs_{self.path}/seq{g_n+1}.txt', 'w') as f:
            f.write('id, x, y, grav, label\n')
            #ordenando groups pelo id da vítima           
            for j in range(len(id_path)):
                    id = id_path[j]
                    x = self.victims[id][0][0]
                    y = self.victims[id][0][1]
                    
                    score = self.victim_id_gravityValue_gravityClass[id]["gravityValue"]*100
                    label = self.victim_id_gravityValue_gravityClass[id]["gravityClass"] + 1
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

        self.plot_clusters(centroids, groups)
        return groups
        

        