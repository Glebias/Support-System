# Используем официальный образ Node.js
FROM node:20-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы package.json и pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN npm install -g pnpm && pnpm install

# Устанавливаем недостающий модуль
RUN pnpm add @fontsource-variable/nunito-sans

# Копируем остальные файлы проекта
COPY . .

# Отключаем ESLint и TypeScript проверки
ENV NEXT_PRIVATE_UNENC_LOAD=1
ENV NEXT_PRIVATE_DISABLE_ESLINT=1
ENV NEXT_PRIVATE_DISABLE_TS=1

# Строим проект
RUN pnpm run build

# Экспонируем порт 3000
EXPOSE 3000

# Запускаем приложение
CMD ["pnpm", "run", "start"]
