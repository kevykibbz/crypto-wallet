# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    sudo \
    openssh-server \
    python3 \
    python3-pip

# Create admin and guest users
RUN useradd -ms /bin/bash admin
RUN echo 'admin:Kevykibbz4578' | chpasswd
RUN useradd -ms /bin/bash guest
RUN echo 'guest:Password@1234' | chpasswd

# Give admin user sudo privileges
RUN usermod -aG sudo admin

# Create SSH directory and add configuration
RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Add welcome.sh to /home/guest and make it executable
COPY welcome.sh /home/guest/welcome.sh
RUN chown guest:guest /home/guest/welcome.sh
RUN chmod +x /home/guest/welcome.sh

# Configure guest user's .bashrc to run welcome.sh on login
RUN echo '/home/guest/welcome.sh' >> /home/guest/.bashrc

# Copy requirements.txt to the working directory
COPY requirements.txt /tmp/requirements.txt

# Install Python packages from requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Expose port 22 for SSH access
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]