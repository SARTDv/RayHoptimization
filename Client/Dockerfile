# Usa la imagen oficial de Node 24.0.1
FROM node:24.0.1-alpine

WORKDIR /app

RUN apk update && apk add git

# Clonar el repositorio
RUN git clone https://github.com/BayronJDv/RayHoptimization.git .

WORKDIR /app/Client

RUN npm install
# Expone el puerto que usa Vite
EXPOSE 5173

# Comando para iniciar la aplicación en modo desarrollo
CMD ["npm", "run", "dev", "--", "--host"]

# Construir la imagen:
# docker build -t bayronj/rayclient .
#comando para correr la imagen
# docker run -p 5173:5173 -e VITE_API_URL=http://localhost:5000 bayronj/rayclient
