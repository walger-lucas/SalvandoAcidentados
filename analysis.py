from sklearn.metrics import silhouette_samples, silhouette_score
import numpy as np

def read_cluster_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = []
    for line in lines[1:]:  # Ignorando o cabeçalho
        values = line.strip().split(',')
        data.append([int(values[0]), float(values[1]), float(values[2]), float(values[3]), int(values[4])])
    return np.array(data)

def calculate_silhouette(data):
    X = data[:, 1:3]  # Usando apenas as colunas x e y
    cluster_labels = data[:, 4]

    silhouette_avg = silhouette_score(X, cluster_labels)
    sample_silhouette_values = silhouette_samples(X, cluster_labels)

    return silhouette_avg, sample_silhouette_values

path = None
while(path == None):
    dataset = input("Informe o dataset(132 ou 225): \n")
    if dataset == "132":
        path = "clusters_data_132v_100x80_TAREFA1"
    elif dataset == "225":
        path = "clusters_data_225v_100x80_TAREFA1"  
    else:
        print("Dataset inválido!\n")

# Lista dos arquivos de texto contendo os clusters
cluster_files = ['cluster1.txt', 'cluster2.txt', 'cluster3.txt', 'cluster4.txt']

silhouette_values = []
for file_path in cluster_files:
    data = read_cluster_data(f"{path}/{file_path}")
    silhouette_avg, sample_silhouette_values = calculate_silhouette(data)
    silhouette_values.extend(sample_silhouette_values)

global_silhouette_avg = np.mean(silhouette_values)
print(f"Silhueta global média: {global_silhouette_avg}")