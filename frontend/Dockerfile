# Use an official Node.js runtime as a parent image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code into the container
COPY . .

# Build the Next.js application
RUN npm run build

# Command to run the application
CMD ["npm", "start"]
