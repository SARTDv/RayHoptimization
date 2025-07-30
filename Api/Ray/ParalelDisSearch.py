import ray
import time
import socket
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score
from itertools import product
import warnings
warnings.filterwarnings('ignore')

# Carga y preparación de los datos
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split

# --- 1. Cargar y preparar los datos ---
# fetch dataset
drug_consumption_quantified = fetch_ucirepo(id=373)
# data (as pandas dataframes)
X = drug_consumption_quantified.data.features
y = drug_consumption_quantified.data.targets

# Binarizar: CL0 y CL1 = No usuario (0), CL2+ = Usuario (1)
y_binary = y['cannabis'].apply(lambda x: 0 if x in ['CL0', 'CL1', 'CL2'] else 1)

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

@ray.remote
def train_and_evaluate_mlp(X_train_data, y_train_data, params):
    """
    Función remota que entrena un modelo MLP con parámetros dados y devuelve su precisión.
    
    Args:
        X_train_data: Datos de entrenamiento (features)
        y_train_data: Etiquetas de entrenamiento
        params: Diccionario con parámetros del modelo MLP
    
    Returns:
        dict: Contiene accuracy, params y hostname donde se ejecutó
    """
    hostname = socket.gethostname()
    task_description = f"Training MLP with params: {params}"
    
    print(f"[{hostname}] Starting task: {task_description}")
    
    try:
        # Crear el modelo MLP con los parámetros dados
        mlp = MLPClassifier(
            random_state=42,
            **params
        )
        
        # Usar validación cruzada estratificada para una evaluación más robusta
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(mlp, X_train_data, y_train_data, cv=cv, scoring='accuracy')
        
        # Calcular la precisión promedio
        mean_accuracy = np.mean(cv_scores)
        std_accuracy = np.std(cv_scores)
        
        print(f"[{hostname}] Completed task: Accuracy = {mean_accuracy:.4f} (+/- {std_accuracy:.4f})")
        
        return {
            'accuracy': mean_accuracy,
            'std_accuracy': std_accuracy,
            'params': params,
            'hostname': hostname,
            'success': True
        }
        
    except Exception as e:
        print(f"[{hostname}] Error in task {task_description}: {str(e)}")
        return {
            'accuracy': 0.0,
            'std_accuracy': 0.0,
            'params': params,
            'hostname': hostname,
            'success': False,
            'error': str(e)
        }

def run_ray_parallel_grid_search(param_grid,X_train_data=X_train, y_train_data=y_train):
    """
    Realiza búsqueda en malla distribuida usando Ray para optimización de hiperparámetros.
    
    Args:
        X_train_data: Datos de entrenamientos (features)
        y_train_data: Etiquetas de entrenamiento
        param_grid: Diccionario con los parámetros a probar
    
    Returns:
        dict: Mejor modelo, mejores parámetros y mejor precisión
    """
    print("=== Iniciando Grid Search Distribuido con Ray ===")
    print(f"Datos de entrenamiento: {X_train_data.shape}")
    print(f"Parámetros a evaluar: {param_grid}")
    
    try:
        # Generar todas las combinaciones de parámetros
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))
        
        print(f"Total de combinaciones a evaluar: {len(param_combinations)}")
        
        # Crear lista de diccionarios de parámetros
        param_dicts = []
        for combination in param_combinations:
            param_dict = dict(zip(param_names, combination))
            param_dicts.append(param_dict)
        
        # Ejecutar tareas en paralelo
        start_time = time.time()
        
        # Lanzar todas las tareas remotas
        futures = []
        for params in param_dicts:
            future = train_and_evaluate_mlp.remote(X_train_data, y_train_data, params)
            futures.append(future)
        
        # Recoger todos los resultados
        print("Ejecutando tareas en paralelo...")
        results = ray.get(futures)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Filtrar solo los resultados exitosos
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if not successful_results:
            raise Exception("Todas las tareas fallaron")
        
        # Encontrar el mejor resultado
        best_result = max(successful_results, key=lambda x: x['accuracy'])
        
        # Entrenar el modelo final con los mejores parámetros
        print("Entrenando modelo final con mejores parámetros...")
        best_model = MLPClassifier(
            random_state=42,
            **best_result['params']
        )
        best_model.fit(X_train_data, y_train_data)
        
        # Mostrar resumen de resultados
        print("\n=== RESUMEN DE RESULTADOS ===")
        print(f"Tiempo total de ejecución: {total_time:.2f} segundos")
        print(f"Tareas exitosas: {len(successful_results)}")
        print(f"Tareas fallidas: {len(failed_results)}")
        
        if failed_results:
            print("Tareas que fallaron:")
            for failed in failed_results:
                print(f"  - Params: {failed['params']}, Error: {failed['error']}")
        
        print(f"\nMejor precisión obtenida: {best_result['accuracy']:.4f} (+/- {best_result['std_accuracy']:.4f})")
        print(f"Mejores parámetros: {best_result['params']}")
        print(f"Ejecutado en nodo: {best_result['hostname']}")
        
        # Mostrar distribución de tareas por nodo
        from collections import Counter
        node_distribution = Counter([r['hostname'] for r in successful_results])
        print(f"\nDistribución de tareas por nodo:")
        for node, count in node_distribution.items():
            print(f"  {node}: {count} tareas")

        return best_result['params'],best_result['accuracy'], best_model

    except Exception as e:
        print(f"Error en grid search: {str(e)}")
        raise e
 