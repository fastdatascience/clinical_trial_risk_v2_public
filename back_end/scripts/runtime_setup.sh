#!/bin/bash

set -e

install_java() {
    echo "Installing Java 17..."
    sudo apt update
    sudo apt install -y openjdk-17-jdk
    java -version
}

install_node_pm2() {
    echo "Installing NVM..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
    export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

    echo "Installing Node.js LTS..."
    nvm install 20
    node -v
    npm -v

    echo "Installing PM2..."
    npm install -g pm2
    pm2 -v
}

install_redis() {
    echo "Installing Redis server..."
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    redis-cli ping
}

install_poetry() {
    echo "Installing Poetry for Python3..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    poetry --version
}

setup_production_environment() {
    echo "Installing Nginx..."
    sudo apt install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx

    echo "Installing Certbot using Python pip..."
    sudo apt install -y python3 python3-venv libaugeas0
    sudo python3 -m venv /opt/certbot/
    sudo /opt/certbot/bin/pip install --upgrade pip
    sudo /opt/certbot/bin/pip install certbot certbot-nginx

    # * Ensure certbot is accessible system-wide
    sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot

    echo "Configuring Nginx..."
    CONFIG_FILE="./nginx/custom_nginx.conf"
    if [[ -f "$CONFIG_FILE" ]]; then
        # * Join all domains into a single space-separated string
        DOMAINS="$*"
        # * Replace {{server_name}} with actual domains in a temporary file
        TEMP_CONFIG="/etc/nginx/sites-available/custom_nginx.conf"
        sed "s/{{server_name}}/${DOMAINS}/" "$CONFIG_FILE" | sudo tee "$TEMP_CONFIG" > /dev/null
        sudo ln -s "$TEMP_CONFIG" /etc/nginx/sites-enabled/
    else
        echo "Custom Nginx configuration file not found. Skipping..."
    fi

    # * Reload Nginx to apply the configuration
    sudo systemctl reload nginx

    echo "Generating SSL certificates for provided domains..."
    sudo certbot --nginx -d "$@"
}

main() {
    install_java
    install_node_pm2
    install_redis
    install_poetry

    # * Check for the --production flag
    if [[ "$1" == "--production" ]]; then
        # * Remove --production from the arguments list
        shift
        if [ -z "$1" ]; then
            echo "Error: No domains provided for SSL certificate generation."
            echo "Usage: ./runtime_setup.sh --production ct-dev.com www.ct-dev.com"
            exit 1
        fi
        setup_production_environment "$@"
    fi

    echo "Setup complete. Java 17, Node.js LTS, PM2, Redis server, Poetry, and optionally Nginx with SSL certificates are installed and configured."
}

main "$@"
