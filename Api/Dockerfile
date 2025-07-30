# Dockerfile para la API Flask con Ray y dependencias
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clonar el repositorio
RUN git clone https://github.com/BayronJDv/RayHoptimization.git .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r Api/requirements.txt
RUN pip install --no-cache-dir ray

WORKDIR /app/Api
# Exponer el puerto de Flask
EXPOSE 5000
EXPOSE 6379  
EXPOSE 8265
EXPOSE 6379

# Iniciar servidor Ray en el puerto 6379
CMD ray start --head --port=6379 --node-ip-address=0.0.0.0 && python app.py

# construir la imagen:
# docker build -t bayronj/rayapi . 
# correr la imagen: 
# docker run -p 5000:5000 -p bayronj/rayapi