#!/bin/bash

# Update the system and install docker
sudo yum update -y
sudo yum install docker expect -y
sudo usermod -a -G docker ec2-user
newgrp docker
sudo systemctl start docker
sudo systemctl enable docker

# Create the expect script for automation
cat << 'EOF' > /tmp/automate_install.sh
#!/usr/bin/expect

# Set timeout to a large value to ensure the script does not timeout
set timeout 300

# Start the command
spawn bash /tmp/install.sh

# Expect a prompt and provide a response
expect {
    "Enter desired number (0-1):" { send "0\r"; exp_continue }
    "Enter desired number (0-1):" { send "0\r"; exp_continue }
    "Does this machine require a proxy to access the Internet? (y/N)" { send "N\r"; exp_continue }
}

# End of expect script
EOF

# Make the expect script executable
chmod +x /tmp/automate_install.sh

# Download the installation script
curl -sSL -o /tmp/install.sh https://get.replicated.com/docker/wickrenterprise/stable

# Run the expect script to handle the install.sh script interaction
/tmp/automate_install.sh
