#!/bin/bash

# Actualiza paquetes e instala Docker desde repositorio de Ubuntu
sudo apt update -y
sudo apt install -y docker.io

# Habilita y arranca el servicio Docker
sudo systemctl enable docker
sudo systemctl start docker

# (Opcional) Permite al usuario ubuntu usar docker sin sudo
sudo usermod -aG docker ubuntu

# Espera que Docker esté completamente listo
sleep 5

# Ejecuta el contenedor con la variable de entorno
docker run -d \
  -e VITE_API_URL="ip:puertodelback" \
  -p 5000:5000 \
  --name mi-api \
  tu_usuario/tu_imagen:tag

# imagen del Cliente
# bayronj/rayhoclient:latest

# imagen del Servidor
# bayronj/rayhoapi:latest

# imagen del Worker
# bayronj/rayhoworker:latest
