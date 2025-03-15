# Use an official Node.js runtime as a parent image
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first (for efficient caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy all files to the container's working directory
COPY . .

# Expose the React development server port
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
