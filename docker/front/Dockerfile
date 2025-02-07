FROM node:18-alpine

# Set work dir
WORKDIR /app

# Copy package.json and package-lock.json
COPY front_end/package*.json .

# Install dependnecies
RUN npm install

# Install serve and vite
RUN npm i -g serve vite

# Copy app
COPY front_end/ .

# Build
RUN npm run build