FROM node:24-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Set work dir for relative paths.
WORKDIR /src

# Copy code from context to image.
COPY . .
