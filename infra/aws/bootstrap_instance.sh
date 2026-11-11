#!/bin/bash
set -euo pipefail

exec > >(tee /var/log/ciudad-conectada-bootstrap.log | logger -t ciudad-conectada-bootstrap -s 2>/dev/console) 2>&1

AWS_REGION="us-east-1"
ARTIFACT_BUCKET="ciudad-conectada-deploy-309487860294-20261110"
DB_SECRET_ARN="arn:aws:secretsmanager:us-east-1:309487860294:secret:rds!db-12777162-df62-4aaf-af5a-6837e23a8a1f-jMOhb2"
APP_SECRET_ID="ciudad-conectada/app-config"
DB_HOST="ciudad-conectada.c2l46k22sllj.us-east-1.rds.amazonaws.com"

dnf install -y nginx python3.12 python3.12-pip mariadb105 unzip

# Small swap file keeps dependency installation stable on a 1 GiB t3.micro.
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 1G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

mkdir -p /opt/ciudad-conectada /var/www/ciudad-conectada
aws s3 cp "s3://${ARTIFACT_BUCKET}/release/ciudad-conectada.zip" /tmp/ciudad-conectada.zip --region "${AWS_REGION}"
unzip -q -o /tmp/ciudad-conectada.zip -d /opt/ciudad-conectada
cp -a /opt/ciudad-conectada/frontend/. /var/www/ciudad-conectada/

python3.12 -m venv /opt/ciudad-conectada/backend/.venv
/opt/ciudad-conectada/backend/.venv/bin/pip install --no-cache-dir -r /opt/ciudad-conectada/backend/requirements.txt

mkdir -p /etc/pki/tls/certs
curl --fail --silent --show-error https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /etc/pki/tls/certs/rds-global-bundle.pem
chmod 644 /etc/pki/tls/certs/rds-global-bundle.pem

aws secretsmanager get-secret-value --secret-id "${DB_SECRET_ARN}" --query SecretString --output text --region "${AWS_REGION}" > /root/cc-db-secret.json
aws secretsmanager get-secret-value --secret-id "${APP_SECRET_ID}" --query SecretString --output text --region "${AWS_REGION}" > /root/cc-app-secret.json
aws s3 cp "s3://${ARTIFACT_BUCKET}/migration/ciudad_conectada.sql" /root/cc-db-dump.sql --region "${AWS_REGION}"
python3.12 - <<'PY'
from pathlib import Path
import re

dump = Path('/root/cc-db-dump.sql')
content = dump.read_bytes()
content = re.sub(rb'DEFINER=`[^`]+`@`[^`]+`\s*', b'', content)
dump.write_bytes(content)
PY

/opt/ciudad-conectada/backend/.venv/bin/python /opt/ciudad-conectada/infra/aws/initialize_instance.py \
  --db-secret /root/cc-db-secret.json \
  --app-secret /root/cc-app-secret.json \
  --dump /root/cc-db-dump.sql \
  --ca /etc/pki/tls/certs/rds-global-bundle.pem \
  --db-host "${DB_HOST}" \
  --env-output /etc/ciudad-conectada.env

rm -f /root/cc-db-secret.json /root/cc-app-secret.json /root/cc-db-dump.sql /tmp/ciudad-conectada.zip
chown -R ec2-user:ec2-user /opt/ciudad-conectada/backend/uploads
chown root:ec2-user /etc/ciudad-conectada.env
chmod 640 /etc/ciudad-conectada.env

install -m 0644 /opt/ciudad-conectada/infra/aws/nginx.conf /etc/nginx/conf.d/ciudad-conectada.conf
rm -f /etc/nginx/conf.d/default.conf
cat > /etc/systemd/system/ciudad-conectada.service <<'UNIT'
[Unit]
Description=Ciudad Conectada FastAPI backend
After=network-online.target
Wants=network-online.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/ciudad-conectada/backend
EnvironmentFile=/etc/ciudad-conectada.env
ExecStart=/opt/ciudad-conectada/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

nginx -t
systemctl daemon-reload
systemctl enable --now ciudad-conectada
systemctl enable --now nginx
echo "Ciudad Conectada bootstrap complete."
