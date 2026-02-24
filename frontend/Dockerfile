FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
# Railway PORT 주입에 맞춤
CMD ["sh", "-c", "npx serve -s dist -l ${PORT:-3000}"]
