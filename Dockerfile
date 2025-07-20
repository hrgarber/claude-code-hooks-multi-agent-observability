# Use Node.js Alpine image that includes npm and bun can be installed
FROM node:20-alpine

# Install dependencies for the build
RUN apk add --no-cache curl bash

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./
COPY apps/server/package*.json ./apps/server/
COPY apps/client/package*.json ./apps/client/

# Install root dependencies (including concurrently)
RUN npm ci || npm install

# Install server dependencies using Bun
WORKDIR /app/apps/server
RUN bun install

# Install client dependencies using npm (fallback to install if no lock file)
WORKDIR /app/apps/client
RUN npm ci || npm install

# Go back to app root
WORKDIR /app

# Copy all source code
COPY . .

# Build client (if needed)
WORKDIR /app/apps/client
RUN npm run build || true

# Go back to app root
WORKDIR /app

# Expose ports
EXPOSE 4000 5173

# Start both services using concurrently
CMD ["npm", "run", "start:all"]