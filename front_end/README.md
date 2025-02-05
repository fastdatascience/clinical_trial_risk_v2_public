# Fast  Data  Science Clinical Trial UI

[![Netlify Status](https://api.netlify.com/api/v1/badges/75ed020a-0623-4851-8868-224e6a6ca101/deploy-status)](https://app.netlify.com/sites/fds-ui/deploys)
![React](https://img.shields.io/badge/React-gray?style=flat&logo=react&logoColor=61DAFB) ![TypeScript](https://img.shields.io/badge/TypeScript-gray?style=flat&logo=typescript&logoColor=3178C6) ![Vite](https://img.shields.io/badge/Vite-gray?style=flat&logo=vite&logoColor=646CFF) ![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-gray?style=flat&logo=tailwindcss&logoColor=06B6D4)

## Running the Project

1. **Clone the Project**
2. `npm install` to install dependencies
3. `npm run dev` to run in development mode

### Temporary Netlify password

``` bash
fdsuilogin
```

### Environment variables

Copy the file `.env.example` to `.env` and fill in the environment variables.

## Run with Docker

Before starting, make sure the ports below are free on the host machine. These ports are mapped on the container to
the host machine.

- `Clinical Trials front-end`: 5173

Follow the steps below to easily run the application with Docker.

#### 1. Clone the repo

```bash
git clone https://github.com/fastdatascience/clinical_trial_risk_v2_public/tree/main/src/front_end
```

#### 2. Environment variables

Copy the file`.env.example` to `.env` and configure the environment variables.

#### 3.1 Build and start containers

The command below will build, (re)create, attach services to containers, and finally start all containers. The
application will be accessible at ` http://127.0.0.1:5173`.

Run a production server:

```bash
docker compose up
```

Or run a development server:

```bash
docker compose -f docker-compose.yml -f docker-compose-dev.yml up
```

#### 3.2 Stop containers

The command below still stop all running containers.

```bash
docker compose stop
```

#### 3.3 Start containers

The command below will start all containers.

```bash
docker compose start
```

#### 3.4 Remove containers

The command below still stop and remove all containers (also networks).
Optionally, you can add `--volumes` to remove the volumes as well.

```bash
docker compose down
```