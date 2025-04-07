import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score

# Função para preparar os dados para Machine Learning
def prepare_data_for_ml(data):
    # Selecionar as colunas relevantes (fechar preço, médias móveis, MACD, etc.)
    features = ['close', 'MA_7', 'MA_22', 'MA_50', 'MACD']
    X = data[features].dropna()  # Remover qualquer valor nulo
    y = (data['close'].shift(-1) > data['close']).astype(int)  # Prever subida ou descida
    
    return X, y

# Função para dividir os dados em conjunto de treino e teste
def train_test_split_data(data):
    X, y = prepare_data_for_ml(data)
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Função para otimizar e treinar os modelos
def train_models(X_train, y_train):
    # Parâmetros para otimização
    rf_params = {
        'n_estimators': [100, 200, 500],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }
    gb_params = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7]
    }
    
    # Otimização do Random Forest
    rf_grid = GridSearchCV(RandomForestClassifier(), rf_params, cv=5, scoring='accuracy')
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_

    # Otimização do Gradient Boosting
    gb_grid = GridSearchCV(GradientBoostingClassifier(), gb_params, cv=5, scoring='accuracy')
    gb_grid.fit(X_train, y_train)
    best_gb = gb_grid.best_estimator_

    print(f"Melhores parâmetros para Random Forest: {rf_grid.best_params_}")
    print(f"Melhores parâmetros para Gradient Boosting: {gb_grid.best_params_}")

    return best_rf, best_gb

# Função para avaliar a performance dos modelos
def evaluate_models(models, X_test, y_test):
    for model_name, model in models.items():
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Acurácia do modelo {model_name}: {accuracy:.2f}")

# Função para prever o movimento dos preços
def predict_price_movement(model, latest_data):
    # Extrair as colunas necessárias para a previsão
    features = ['close', 'MA_7', 'MA_22', 'MA_50', 'MACD']
    
    # Certificar-se de que os nomes das colunas estão preservados
    latest_features = latest_data[features].dropna().tail(1)
    
    # Usar o modelo treinado para prever o próximo movimento de preço
    prediction = model.predict(latest_features)
    
    return "subida" if prediction == 1 else "descida"
