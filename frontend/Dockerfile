FROM node:18 AS Build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY ./ ./

RUN npm run build


FROM nginx

COPY --from=build /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]

