# Deployment (Ubuntu 24)

## 1. Install dependencies on server

### 1.1 Update package index

```bash
sudo apt update
```

### 1.2 Install NodeJS and NPM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 20.18.0
node -v
npm -v
```

### 1.3 Install PM2

```bash
sudo npm install -g pm2
pm2 -v
```

### 1.4 Install Redis

```bash
sudo apt install redis-server -y
redis-server --version
sudo systemctl restart redis
sudo systemctl status redis
sudo systemctl enable --now redis-server # To start Redis on reboot
```

### 1.5 Install Java

```bash
sudo apt install openjdk-17-jre
sudo apt install openjdk-17-jdk
java --version
```

### 1.6 Install Apache Maven

```bash
sudo apt install maven -y
mvn -version
```

### 1.7 Install Poetry

```bash
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.5 python3 -
```

Open `.bashrc`:

```bash
nano ~/.bashrc
```

Add the following: `export PATH="/home/azureuser/.local/bin:$PATH"`.

Then:

```bash
source ~/.bashrc
poetry --version
```

### 1.8 Install Make

```bash
sudo apt-get install build-essential
make --version
```

### 1.9 Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 1.10 Install Certbot

```bash
sudo apt install -y python3 python3-venv libaugeas0
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
```

### 1.11 Install wkhtmltopdf

`wkhtmltopdf` is required for the python package `pdfkit` to function correctly, it is a wrapper for `wkhtmltopdf`.
`pdfkit` is used for generating the analysis report in PDF.

```bash
sudo apt install -y wkhtmltopdf
```

## 2. Install and run application

### 2.1 Copy application to server

Clone the application on your local machine:

```bash
cd ~
git clone --recurse-submodules https://github.com/fastdatascience/clinical_trial_risk_v2_public/tree/main/src/back_end
```

To make sure you have the latest version of the submodule:

```bash
cd ~/clinical_trials_backend
git submodule update --remote
```

Use a software such as WinSCP or FileZilla and transfer the application to `~/clinical_trials_backend` on the server,
then cd into `~/clinical_trials_backend`.

### 2.2 Environment variables

copy the file `.env.example` to `.env` and fill in the environment variables.

### 2.3 Install application

```bash
cd ~/clinical_trials_backend
poetry shell
poetry install --only main --no-interaction --no-root
```

### 2.4 Download classifiers

Download classifiers:

```bash
cd ~/clinical_trials_backend
poetry shell
python cli --download-models
```

The classifiers will be downloaded to `/tmp`.

### 2.5 PM2 services

#### 2.5.1 Create and run PM2 services

```bash
cd ~/clinical_trials_backend

# It is important to activate the environment before creating the PM2 services
poetry shell

# Only run the following command once to create and start the PM2 services
pm2 start ecosystem.config.js

pm2 save

# After running this command, you will be suggested to run another command for automatic startup with systemd
pm2 startup
```

#### 2.5.2 Stop PM2 services

```bash
pm2 stop all
```

#### 2.5.3 Start PM2 services

```bash
pm2 start all
```

#### 2.5.4 Restart PM2 services

```bash
pm2 restart all
```

## Nginx

Logs:

```bash
less /var/log/nginx/error.log
```
