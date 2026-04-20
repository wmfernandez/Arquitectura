FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all files
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Start the dev server and expose it to the Docker network
CMD ["npm", "run", "dev", "--", "--host"]
