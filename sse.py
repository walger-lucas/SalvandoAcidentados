import pandas as pd
from io import StringIO

# Calculadora bem sem vergonha de SSE

# Recebe o nome do dataset
dataset = input("Insert dataset folder: ")
# Recebe o cluster
cluster = input("Insert cluster numer: ")

# Abre o arquivo desejado
file = open(f"{dataset}/cluster{cluster}.txt", "r")
content = file.read()

# Carregando os dados em um DataFrame
df = pd.read_csv(StringIO(content), sep=',\s+', engine='python')

# Calculando o centróide
centroid = df.mean()[['x', 'y']]

# Calculando a distância quadrada de cada ponto para o centróide e somando
sse = ((df[['x', 'y']] - centroid)**2).sum(axis=1).sum()
print(sse)
file.close()