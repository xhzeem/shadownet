FROM alpine:3.14

# Install all necessary packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    apache2 \
    apache2-utils \
    bash \
    mysql \
    mysql-client \
    openssh \
    vsftpd \
    redis \
    openldap \
    openldap-clients \
    supervisor \
    curl \
    iputils \
    grep \
    sed

# Install older bash version for Shellshock (manual install as it's removed from main repos)
# Note: For Alpine 3.14, we'll try to use a specifically vulnerable version or mock it if unavailable.
# Actually, let's use a specialized base for shellshock or just ensure the bash is vulnerable.
# For simplicity in a single image, we will install a known vulnerable version or use a trick.
RUN apk add --no-cache bash=5.1.4-r0 || true 
# Re-adjusting Shellshock strategy: We'll use a Debian-based image for better package control for vulnerabilities.

FROM debian:bullseye-slim

# Install dependencies and setup LDAP selections
RUN apt-get update && \
    echo "slapd slapd/domain string shadownet.local" | debconf-set-selections && \
    echo "slapd slapd/internal_admin_password password admin" | debconf-set-selections && \
    echo "slapd slapd/internal_admin_password_again password admin" | debconf-set-selections && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    apache2 \
    bash \
    mariadb-server \
    openssh-server \
    vsftpd \
    redis-server \
    supervisor \
    curl \
    iputils-ping \
    sqlite3 \
    libtinfo5 \
    slapd \
    ldap-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*


# Install vulnerable bash for Shellshock (CVE-2014-6271)
RUN curl -L -o bash.deb https://snapshot.debian.org/archive/debian/20140901T000000Z/pool/main/b/bash/bash_4.2+dfsg-0.1_amd64.deb \
    && dpkg -i bash.deb \
    && rm bash.deb

# Setup Python environment
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Setup Flask App
COPY app.py .
COPY templates/ templates/

# Setup Apache for CGI (Shellshock)
RUN a2enmod cgi
COPY cgi-bin/ /usr/lib/cgi-bin/
RUN chmod +x /usr/lib/cgi-bin/vulnerable.cgi
RUN sed -i 's/Listen 80/Listen 80/g' /etc/apache2/ports.conf

# Setup SSH
RUN mkdir /var/run/sshd
RUN useradd -m -s /bin/bash service && echo "service:password" | chpasswd
COPY ssh/notes.txt /home/service/notes.txt
COPY ssh/bash_history /home/service/.bash_history
RUN chown service:service /home/service/notes.txt /home/service/.bash_history
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Setup MySQL
RUN mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld
COPY scripts/mysql_init.sql /tmp/mysql_init.sql
RUN service mariadb start && \
    mysql < /tmp/mysql_init.sql && \
    service mariadb stop

# Setup Redis (Unauthenticated)
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
RUN sed -i 's/protected-mode yes/protected-mode no/' /etc/redis/redis.conf
COPY scripts/populate_redis.sh /usr/local/bin/populate_redis.sh
RUN chmod +x /usr/local/bin/populate_redis.sh

# Setup FTP (Anonymous)
RUN mkdir -p /var/ftp/pub && chown -R ftp:ftp /var/ftp
COPY scripts/vsftpd.conf /etc/vsftpd.conf
COPY scripts/config.bak /var/ftp/pub/config.bak
RUN echo "ShadowNet{FTP_An0n_Access_Succ3ss}" > /var/ftp/pub/flag.txt

# Setup LDAP (Anonymous)
COPY ldap/data.ldif /tmp/data.ldif
COPY scripts/ldap_init.sh /usr/local/bin/ldap_init.sh
RUN chmod +x /usr/local/bin/ldap_init.sh
# LDAP re-configuration for non-interactive setup is already handled above




# Setup Supervisor
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose all ports
EXPOSE 80 5000 21 22 3306 6379 389

# Entrypoint
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
