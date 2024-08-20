# import numpy as np
# import tensorflow as tf
# from tensorflow.keras import Sequential
# from tensorflow.keras.layers import Dense, Dropout
# from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# # Leitura do arquivo
# file_path = 'datasets/4000.txt'# Substitua pelo caminho do seu arquivo# Inicializar listas para características e rótulos
# X = []
# y = []

# # Ler e processar cada linhawithopen(file_path, 'r') as file:
# with open(file_path, 'r') as file:
#     for line in file:
#         # Separar os valores por vírgula
#         values = line.strip().split(',')
        
#         # Extrair as características (colunas 1 a 6) e o rótulo (última coluna)
#         features = list(map(float, values[3:6]))  # Converta as características para float
#         label = int(values[7])  # Converta o rótulo para inteiro# Adicionar as características e rótulo às listas
#         label = label - 1  # Ajustar o rótulo para começar em 0
#         X.append(features)
#         y.append(label)

# # Converter listas para arrays numpy
# X = np.array(X)
# y = np.array(y)



# # Transformando rótulos em categorias (one-hot encoding)
# y_train = tf.keras.utils.to_categorical(y, num_classes=4)

# # Definindo o modelo aprimorado para maior assertividade
# model = Sequential([
#     Dense(256, input_shape=(3,), activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),  # Primeira camada oculta com mais neurônios
#     Dropout(0.4),
#     Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),                    # Segunda camada oculta
#     Dropout(0.4),
#     Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),                     # Terceira camada oculta
#     Dropout(0.3),
#     Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),                     # Quarta camada oculta
#     Dropout(0.3),
#     Dense(4, activation='softmax')                                                                        # Camada de saída
# ])

# # Compilando o modelo com um otimizador Adam ajustado
# model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
#               loss='categorical_crossentropy', metrics=['accuracy'])
# print('Modelo compilado com sucesso!')

# # Callbacks para melhorar o treinamento
# #early_stopping = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True)
# #reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=10, min_lr=0.00001)

# # Treinando o modelo com mais épocas e potencialmente mais batch_size
# history = model.fit(X, y_train, epochs=200000, batch_size=64, validation_split=0.2)
#                     #,callbacks=[early_stopping, reduce_lr])
# print('Modelo treinado com sucesso!')

# # Salvando o modelo treinado
# model.save('classifier-200000-epochs-no-callbacks.h5')
# print('Modelo salvo com sucesso!')

import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import KFold

# Função para criar diferentes modelos
def create_model(layers, activation, learning_rate):
    model = Sequential()
    for neurons in layers:
        model.add(Dense(neurons, activation=activation))
        model.add(Dropout(0.3))
    model.add(Dense(4, activation='softmax'))
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Função para executar treinamento com validação cruzada
def train_and_evaluate(X, y, model_configs, k_folds=5):

    
    results = []
    for i, config in enumerate(model_configs):
        print(f'Treinando modelo {i+1} com configuração: {config}')
        kf = KFold(n_splits=k_folds, shuffle=True)
        fold_accuracies = []
        
        for train_index, val_index in kf.split(X):
            X_train, X_val = X[train_index], X[val_index]
            y_train, y_val = y[train_index], y[val_index]
            
            model = create_model(config['layers'], config['activation'], config['learning_rate'])
            early_stopping = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=10, min_lr=0.00001)
            
            model.fit(X_train, y_train, epochs=500, batch_size=64, validation_data=(X_val, y_val),
                      callbacks=[early_stopping, reduce_lr], verbose=0)
            
            val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
            fold_accuracies.append(val_acc)
        
        avg_accuracy = np.mean(fold_accuracies)
        results.append((config, avg_accuracy))
        model.save(f'classifier_models/model_{i+1}.h5')
        with open("classifier_models/models.txt", "a") as file:
            file.write(f'model_{i+1}.h5:\nConfig: {str(model_configs[i])}\nAccuracy: {avg_accuracy:.4f}\n--------------------------------------\n')
        print(f'Modelo {i+1} treinado e salvo com acurácia média de {avg_accuracy:.4f}')
    
    return results

# Carregar e preparar os dados
file_path = 'datasets/4000.txt'
X, y = [], []

with open(file_path, 'r') as file:
    for line in file:
        values = line.strip().split(',')
        features = list(map(float, values[3:6]))
        label = int(values[7]) - 1
        X.append(features)
        y.append(label)

X = np.array(X)
y = np.array(y)
y_train = tf.keras.utils.to_categorical(y, num_classes=4)

# Definições das configurações dos modelos
model_configs = [
    {'layers': [128, 64], 'activation': 'relu', 'learning_rate': 0.001},
    {'layers': [256, 128, 64], 'activation': 'relu', 'learning_rate': 0.0005},
    {'layers': [128, 128, 128], 'activation': 'tanh', 'learning_rate': 0.001},
    {'layers': [256, 128, 64, 32], 'activation': 'relu', 'learning_rate': 0.0005},
    {'layers': [512, 256], 'activation': 'relu', 'learning_rate': 0.0001},
    {'layers': [128, 64, 32], 'activation': 'relu', 'learning_rate': 0.001},
    {'layers': [256, 128, 64, 32, 16], 'activation': 'relu', 'learning_rate': 0.0005},
    {'layers': [512, 256, 128], 'activation': 'relu', 'learning_rate': 0.0001},
    {'layers': [128, 128, 128, 128], 'activation': 'tanh', 'learning_rate': 0.001},
    {'layers': [256, 128, 64, 32, 16, 8], 'activation': 'relu', 'learning_rate': 0.0005}
]

# Treinar e avaliar os modelos
results = train_and_evaluate(X, y_train, model_configs, k_folds=5)

# Exibir os resultados
for i, (config, accuracy) in enumerate(results):
    print(f'Modelo {i+1} - Configuração: {config} - Acurácia Média: {accuracy:.4f}')
