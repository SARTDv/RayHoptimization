# Instrucciones para Despliegue de Ray-HOptimization en AWS

## 1. Crear la VPC y Subredes
- Crea una VPC (ejemplo: `rayhov1`).
- Crea dos subredes: una pública y una privada.
- Configura un NAT Gateway para permitir que las instancias en la subred privada accedan a internet.

## 2. Crear Security Groups

### 2.1. client-sg (para la instancia cliente)
- Inbound:
  - HTTP (80) desde 0.0.0.0/0
  - HTTPS (443) desde 0.0.0.0/0
  - SSH (22) solo desde tu IP
  - TCP (5173) desde 0.0.0.0/0 (para acceso al frontend)

### 2.2. head-sg (para la instancia head de Ray)
- Inbound:
  - Permitir todo el tráfico desde `client-sg`
  - Permitir todo el tráfico desde `workers-internal-sg`

### 2.3. workers-internal-sg (para los workers de Ray)
- Inbound:
  - Permitir todo el tráfico desde `head-sg`
  - Permitir todo el tráfico desde `workers-internal-sg`

## 3. Lanzar Instancias

### 3.1. Instancia Head (Ray Head Node)
- AMI recomendada: Ubuntu Server
- Ubicación: subred privada
- Security Group: `head-sg`
- Script de inicio (user data): `headinit.bash`

### 3.2. Instancia Cliente
- AMI recomendada: Ubuntu Server
- Ubicación: subred pública
- Security Group: `client-sg`
- Script de inicio (user data): `workerinit.bash`

> **Nota:** Desde esta instancia puedes conectarte por SSH y ejecutar el script `peticion.py` usando la IP privada de la instancia head, o acceder al frontend si lo tienes desplegado.

### 3.3. Instancias Worker
- AMI recomendada: Ubuntu Server
- Ubicación: subred privada
- Security Group: `workers-internal-sg`
- Script de inicio (user data): `worker.bash`

## 4. Pruebas y Ejecución

- Una vez desplegadas las instancias, puedes probar la ejecución secuencial y paralela conectándote por SSH a la instancia cliente y ejecutando `peticion.py`.
- Para pruebas distribuidas completas, asegúrate de que los workers estén corriendo y conectados al head node.
- El frontend puede ser accedido desde el navegador usando la IP pública de la instancia cliente (puerto 5173).

- ray start --address=172.17.0.2:6379 && tail -f /dev/null
- export VITE_API_URL=https://tu-api-en-ec2.com

