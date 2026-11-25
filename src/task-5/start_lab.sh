#!/bin/bash
# Запуск только внутри учебного Linux-контейнера.
set -euo pipefail
[[ -f /.dockerenv ]] || { echo 'Нужен учебный Docker-контейнер.' >&2; exit 1; }
mkdir -p /var/log/app /opt/backups /run/lock
install -m 0750 /work/backup_and_clean.sh /usr/local/sbin/backup_and_clean.sh
# Первая задача — резервное копирование в 02:00, вторая — запрос к приложению каждую минуту.
{
    cat /work/cron-root.txt
    printf '* * * * * /usr/bin/curl -fsS --max-time 15 http://127.0.0.1:8080/ >/dev/null 2>&1\n'
} | crontab -
export APP_LOG_FILE=/var/log/app/app.log
export APP_LOCK_FILE=/run/lock/app-backup.lock
php -S 0.0.0.0:8080 -t /work/hosting/public &
php_pid=$!
/usr/sbin/cron -f &
cron_pid=$!
trap 'kill "$php_pid" "$cron_pid" 2>/dev/null || true' EXIT TERM INT
wait -n "$php_pid" "$cron_pid"
