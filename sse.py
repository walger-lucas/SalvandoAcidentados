import pandas as pd
from io import StringIO

# Os dados do cluster fornecido
data = """id, x, y, grav, label
1, -25, 14, 50.0, 3
2, -25, 41, 50.0, 3
3, -25, 44, 40.0, 3
4, -23, 15, 30.0, 3
5, -23, 42, 20.0, 4
6, -21, 45, 35.0, 3
7, -21, 46, 10.0, 4
10, -20, 7, 45.0, 3
11, -20, 10, 15.0, 4
13, -18, 6, 60.0, 2
14, -18, 36, 45.0, 3
20, -11, 6, 60.0, 2
24, -7, 9, 40.0, 3
35, 3, 35, 20.0, 4
37, 5, 25, 40.0, 3
45, 11, 17, 35.0, 3
47, 12, -10, 30.0, 3
48, 12, -1, 35.0, 3
49, 12, 15, 30.0, 3
50, 13, 14, 45.0, 3
53, 14, 19, 40.0, 3
54, 15, 16, 40.0, 3
56, 16, 4, 25.0, 4
57, 16, 8, 40.0, 3
63, 19, 18, 15.0, 4
70, 22, 16, 15.0, 4
71, 23, 17, 55.0, 2
78, 28, 12, 25.0, 4
79, 29, 9, 40.0, 3"""

# Carregando os dados em um DataFrame
df = pd.read_csv(StringIO(data), sep=',\s+', engine='python')

# Calculando o centróide
centroid = df.mean()[['x', 'y']]

# Calculando a distância quadrada de cada ponto para o centróide e somando
sse = ((df[['x', 'y']] - centroid)**2).sum(axis=1).sum()
print(sse)
