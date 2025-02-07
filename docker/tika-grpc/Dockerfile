FROM maven:3.9.1-eclipse-temurin-17

# Set workdir
WORKDIR /app

# Copy tika grpc
COPY back_end/tika-grpc .

# Build
RUN mvn clean package
