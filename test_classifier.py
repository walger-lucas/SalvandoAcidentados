# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model

# # Carregar o modelo treinado
# model = load_model('classifier-200000-epochs-no-callbacks.h5')

# # Leitura do arquivo de teste
# file_path = 'datasets/800.txt'# Substitua pelo caminho do seu arquivo# Inicializar listas para características e rótulos
# X_test = []
# y_test = []

# # Ler e processar cada linha
# with open(file_path, 'r') as file:
#     for line in file:
#         # Separar os valores por vírgula
#         values = line.strip().split(',')
        
#         # Extrair as características (colunas 3 a 5) e o rótulo esperado (coluna 7)
#         features = list(map(float, values[3:6]))  # Converta as características para float
#         label = int(values[7]) - 1# Converta o rótulo para o intervalo 0-3# Adicionar as características e rótulo esperado às listas
#         X_test.append(features)
#         y_test.append(label)

# # Converter listas para arrays numpy
# X_test = np.array(X_test)
# y_test = np.array(y_test)

# # Fazer predições com o modelo
# predictions = model.predict(X_test)

# # Converter as predições para rótulos (classe com maior probabilidade)
# predicted_classes = np.argmax(predictions, axis=1)

# # Comparar predições com rótulos esperados
# correct_predictions = np.sum(predicted_classes == y_test)
# incorrect_predictions = np.sum(predicted_classes != y_test)

# # Exibir os resultadosprint(f'Classificações corretas: {correct_predictions}')
# print(f'Classificações incorretas: {incorrect_predictions}')
# print(f'Acurácia: {correct_predictions / len(y_test) * 100:.2f}%')

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Função para testar um modelo em dados de teste
def test_model(model_path, test_data_path):
    model = load_model(model_path)
    
    # Carregar dados de teste
    X_test, y_test = [], []
    with open(test_data_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            features = list(map(float, values[3:6]))
            label = int(values[7]) - 1
            X_test.append(features)
            y_test.append(label)
    
    X_test = np.array(X_test)
    y_test = np.array(y_test)
    
    # Fazer predições com o modelo
    predictions = model.predict(X_test)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Comparar predições com rótulos esperados
    correct_predictions = np.sum(predicted_classes == y_test)
    incorrect_predictions = np.sum(predicted_classes != y_test)
    
    accuracy = correct_predictions / len(y_test) * 100
    print(f'Classificações corretas: {correct_predictions}')
    print(f'Classificações incorretas: {incorrect_predictions}')
    print(f'Acurácia: {accuracy:.2f}%')
    return accuracy

# Testar todos os modelos salvos
model_files = ['model_1.h5', 'model_2.h5', 'model_3.h5', 'model_4.h5']
for i in range(10):
    print(f'\nTestando model_{i+1}.h5:')
    test_model(f"classifier_models/model_{i+1}.h5", 'datasets/800.txt')
