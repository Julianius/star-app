FROM jenkins/jenkins:lts-jdk8
USER root
ARG HOST_UID=1001
ARG HOST_GID=998
RUN apt-get update && \
    apt-get install -y docker.io iputils-ping telnet curl wget unzip vim && \
    usermod -aG docker jenkins && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    apt-get install sudo && \
    echo 'root:123456' | sudo chpasswd && \
    wget --quiet https://releases.hashicorp.com/terraform/1.0.9/terraform_1.0.9_linux_amd64.zip && \
    unzip terraform_1.0.9_linux_amd64.zip && \
    mv terraform /usr/bin && \
    rm terraform_1.0.9_linux_amd64.zip
USER jenkins