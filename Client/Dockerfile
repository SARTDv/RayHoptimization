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