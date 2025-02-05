# Docker Deployment (Ubuntu 24)

## 1. Install Docker on server

### 1.1 Add Docker's official GPG key:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### 1.2 Add the repository to Apt sources:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### 1.3 Install Docker

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 1.4 Verify installation

```bash
sudo docker run hello-world
```

### 1.5 Add user to Docker group

```bash
sudo usermod -aG docker [USER]
```

## 2. Copy application to server

### 2.1 Clone the repo

On your local machine:

```bash
cd ~
git clone --recurse-submodules https://github.com/fastdatascience/clinical_trial_risk_v2_public/tree/main/src/back_end
```

To make sure you have the latest version of the submodule:

```bash
cd ~/clinical_trials_backend
git submodule update --remote
```

### 2.2 Update clinical_trials_core submodule

To make sure the latest version of `clinical_trials_core` is in use.

On your local machine:

```bash
cd ~/clinical_trials_backend/clinical_trials_core
git pull origin main
```

### 2.3 Download classifiers

Download classifiers on your local machine:

```bash
# Create the dir classifiers at the root of the project
cd ~/clinical_trials_backend
mkdir classifiers

# Install the core package
pip install ./clinical_trials_core

# Download classifiers
python3 cli --download-models --download-path /home/[YOUR_USERNAME]/clinical_trials_backend/classifiers
```

### 2.4 Copy `clinical_trials_backend` to the server

Use a software such as `WinSCP` or `FileZilla` to transfer the dir.

- Copy `~/clinical_trials_backend` to the home dir on the server.

### 2.5 Environment variables

Copy `.env.example` to `.env` and configure the env variables.

On server:

```bash
cd ~/clinical_trials_backend
cp .env.example .env
```

## 3. Run application on server

### 3.1 Run containers

```bash
sudo docker compose up -d
```

### 3.2 Restore db dump (optional)

Create db backup as `.tar` file and save it to your home dir.
You can use `pgAdmin` to create the dump file.
After that you can copy the db dump to the server.

On your local machine:

```bash
cd ~
scp db_dump.tar [USER]@[IP]:~/
```

Restore db dump.

On server:

```bash
docker exec -i CONTAINER_ID pg_restore -U postgres -v -d clinical_trials < ~/db_dump.tar
```

### 3.3 Nginx

Setup `Nginx` on the server to serve the API that is running on port `5000` to the outside on port `80` and `443`.

### 3.4 Other useful Docker commands

See running containers (add `--all` to see all containers).

```bash
sudo docker ps
```

See all images.

```bash
sudo docker image ls
```

Stop containers.

```bash
sudo docker compose stop
```

## 4. Manually update API on server

*Note: Manually updating the API on the server is normally not required as deployment is done by a GitHub workflow.*

After pulling changes, you must build a new image and restart the `api` container.

The following command will build a new image and only restart the `api` container.

```bash
sudo docker compose up --no-deps -d --build api
```

To also restart the `Celery` containers, you can add `celery_worker` and `celery_beat` after `--build`.
