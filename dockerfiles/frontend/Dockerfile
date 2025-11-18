#FROM node:lts-alpine
#
#MAINTAINER arkanister "arkanister.dev@gmail.com"
#
## install simple http server for serving static content
#RUN npm install -g http-server
#
#WORKDIR /app
#
## copy both 'package.json' and 'package-lock.json' (if available)
#COPY frontend/ .
#
## install project dependencies
#RUN npm install
#
## build app for production with minification
#RUN npm run build
#
#ENTRYPOINT ["http-server", "dist"]
#EXPOSE 8080




FROM node:lts-alpine
WORKDIR /app

# 全域安裝 Vue CLI（或 Vite CLI，看你的專案）
RUN npm install -g @vue/cli

# 安裝專案依賴（不含 build）
COPY frontend/package*.json ./
RUN npm install

# 啟動開發伺服器
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0"]
EXPOSE 8080
