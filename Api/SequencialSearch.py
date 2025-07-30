import time
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from itertools import product
import warnings
warnings.filterwarnings('ignore')

# Carga y preparación de los datos (mismo que el distribuido)
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split

# --- 1. Cargar y preparar los datos ---
drug_consumption_quantified = fetch_ucirepo(id=373)
X = drug_consumption_quantified.data.features
y = drug_consumption_quantified.data.targets

# Binarizar: CL0 y CL1 = No usuario (0), CL2+ = Usuario (1)
y_binary = y['cannabis'].apply(lambda x: 0 if x in ['CL0', 'CL1', 'CL2'] else 1)

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

def train_and_evaluate_mlp_sequential(X_train_data, y_train_data, params, task_num, total_tasks):
    """
    Función secuencial que entrena un modelo MLP con parámetros dados y devuelve su precisión.
    
    Args:
        X_train_data: Datos de entrenamiento (features)
        y_train_data: Etiquetas de entrenamiento
        params: Diccionario con parámetros del modelo MLP
        task_num: Número de tarea actual
        total_tasks: Total de tareas a ejecutar
    
    Returns:
        dict: Contiene accuracy, params y metadata
    """
    task_description = f"Training MLP with params: {params}"
    
    print(f"[SEQUENTIAL] Task {task_num}/{total_tasks}: {task_description}")
    
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
        
        print(f"[SEQUENTIAL] Task {task_num}/{total_tasks} completed: Accuracy = {mean_accuracy:.4f} (+/- {std_accuracy:.4f})")
        
        return {
            'accuracy': mean_accuracy,
            'std_accuracy': std_accuracy,
            'params': params,
            'task_number': task_num,
            'success': True
        }
        
    except Exception as e:
        print(f"[SEQUENTIAL] Error in task {task_num}/{total_tasks} - {task_description}: {str(e)}")
        return {
            'accuracy': 0.0,
            'std_accuracy': 0.0,
            'params': params,
            'task_number': task_num,
            'success': False,
            'error': str(e)
        }

def sequential_grid_search(param_grid, X_train_data=X_train, y_train_data=y_train):
    """
    Realiza búsqueda en malla de manera secuencial para optimización de hiperparámetros.
    
    Args:
        X_train_data: Datos de entrenamiento (features)
        y_train_data: Etiquetas de entrenamiento
        param_grid: Diccionario con los parámetros a probar
    
    Returns:
        tuple: Mejores parámetros, mejor precisión y modelo entrenado
    """
    print("=== Iniciando Grid Search Secuencial ===")
    print(f"Datos de entrenamiento: {X_train_data.shape}")
    print(f"Parámetros a evaluar: {param_grid}")
    
    try:
        # Generar todas las combinaciones de parámetros
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))
        
        total_combinations = len(param_combinations)
        print(f"Total de combinaciones a evaluar: {total_combinations}")
        
        # Crear lista de diccionarios de parámetros
        param_dicts = []
        for combination in param_combinations:
            param_dict = dict(zip(param_names, combination))
            param_dicts.append(param_dict)
        
        print("Iniciando evaluación secuencial...")
        print("-" * 60)
        
        # Ejecutar tareas de manera secuencial
        start_time = time.time()
        results = []
        
        for i, params in enumerate(param_dicts, 1):
            # Mostrar progreso cada 10 tareas o en tareas importantes
            if i % 10 == 0 or i == 1 or i == total_combinations:
                elapsed_time = time.time() - start_time
                estimated_total = (elapsed_time / i) * total_combinations if i > 0 else 0
                remaining_time = estimated_total - elapsed_time
                
                print(f"\n--- PROGRESO: {i}/{total_combinations} ({i/total_combinations*100:.1f}%) ---")
                print(f"Tiempo transcurrido: {elapsed_time:.2f}s")
                print(f"Tiempo estimado restante: {remaining_time:.2f}s")
                print(f"Tiempo total estimado: {estimated_total:.2f}s")
            
            # Ejecutar tarea individual
            result = train_and_evaluate_mlp_sequential(
                X_train_data, y_train_data, params, i, total_combinations
            )
            results.append(result)
        
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
        print("\n" + "="*60)
        print("Entrenando modelo final con mejores parámetros...")
        best_model = MLPClassifier(
            random_state=42,
            **best_result['params']
        )
        best_model.fit(X_train_data, y_train_data)
        
        # Mostrar resumen de resultados
        print("\n=== RESUMEN DE RESULTADOS SECUENCIAL ===")
        print(f"Tiempo total de ejecución: {total_time:.2f} segundos")
        print(f"Tiempo promedio por tarea: {total_time/total_combinations:.2f} segundos")
        print(f"Tareas exitosas: {len(successful_results)}")
        print(f"Tareas fallidas: {len(failed_results)}")
        
        if failed_results:
            print("Tareas que fallaron:")
            for failed in failed_results:
                print(f"  - Tarea {failed['task_number']}: {failed['params']}, Error: {failed['error']}")
        
        print(f"\nMejor precisión obtenida: {best_result['accuracy']:.4f} (+/- {best_result['std_accuracy']:.4f})")
        print(f"Mejores parámetros: {best_result['params']}")
        print(f"Encontrado en tarea número: {best_result['task_number']}")
        
        # Mostrar top 5 mejores resultados
        top_5_results = sorted(successful_results, key=lambda x: x['accuracy'], reverse=True)[:5]
        print(f"\nTop 5 mejores configuraciones:")
        for i, result in enumerate(top_5_results, 1):
            print(f"  {i}. Accuracy: {result['accuracy']:.4f} - Params: {result['params']}")
        
        return best_result['params'], best_result['accuracy'], best_model
        
    except Exception as e:
        print(f"Error en grid search secuencial: {str(e)}")
        raise e