import ray
import time

def initialize_ray_cluster():
    """
    Inicializa el cluster de Ray con reintentos automáticos.
    
    Esta función intenta conectarse al cluster de Ray hasta 10 veces,
    esperando 5 segundos entre cada intento. Si no puede conectarse
    después de todos los intentos, lanza una excepción.
    
    Raises:
        RuntimeError: Si no se puede conectar al cluster después de los reintentos máximos
    
    Returns:
        None
    """
    max_retries = 10
    retry_delay = 5
    
    print("Inicializando conexión con el cluster de Ray...")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Intento {attempt}/{max_retries}: Conectando al cluster de Ray...")
            ray.init(address="auto", ignore_reinit_error=True)
            print("✅ Conexión exitosa con el cluster de Ray")
            return
            
        except ConnectionError as e:
            print(f"❌ Error de conexión (intento {attempt}/{max_retries}): {str(e)}")
            
            if attempt < max_retries:
                print(f"⏳ Esperando {retry_delay} segundos antes del siguiente intento...")
                time.sleep(retry_delay)
            else:
                print("💥 Se agotaron todos los intentos de conexión")
                
        except Exception as e:
            print(f"❌ Error inesperado (intento {attempt}/{max_retries}): {str(e)}")
            
            if attempt < max_retries:
                print(f"⏳ Esperando {retry_delay} segundos antes del siguiente intento...")
                time.sleep(retry_delay)
            else:
                print("💥 Se agotaron todos los intentos de conexión")
    
    # Si llegamos aquí, significa que todos los intentos fallaron
    error_msg = f"No se pudo conectar al cluster de Ray después de {max_retries} intentos"
    print(f"🚨 {error_msg}")
    raise RuntimeError(error_msg)