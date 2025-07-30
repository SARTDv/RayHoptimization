# Etapa 1: construir React app con Vite
FROM node:18-alpine AS builder

# Instalar git
RUN apk add --no-cache git

# Clonar tu repositorio (ajusta URL si es privado)
RUN git clone https://github.com/SARTDv/RayHoptimization.git /app

# Establecer directorio de trabajo
WORKDIR /app/Client

# Instalar dependencias y compilar
RUN npm install && npm run build

# Etapa 2: imagen liviana solo para servir el frontend
FROM nginx:alpine

# Copiar archivos compilados desde el builder
COPY --from=builder /app/Client/dist /usr/share/nginx/html

# Copiar plantilla nginx
COPY nginx.template /etc/nginx/nginx.template

# Configurar NGINX con variable de entorno API_HOST
CMD envsubst '${API_HOST}' < /etc/nginx/nginx.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
