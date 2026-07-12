FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source
COPY . .

# Build the React app
RUN npm run build

# Install a lightweight static server
RUN npm install -g serve

# Railway provides PORT automatically
EXPOSE 8080

CMD sh -c "serve -s dist -l ${PORT:-8080}"