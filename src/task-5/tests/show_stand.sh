#!/bin/bash
set -euo pipefail
[[ -f /.dockerenv ]] || exit 1
printf 'Система: '; uname -a
printf 'Часовой пояс и время: '; date '+%F %T %Z %z'
printf '\nУстановленное расписание root:\n'; crontab -l
printf '\nHTTP-запрос к приложению:\n'
curl -fsS http://127.0.0.1:8080/
printf '\nФайл до очистки:\n'
stat -c 'inode=%i size=%s mode=%a owner=%U' /var/log/app/app.log
printf '\nЗапуск скрипта:\n'
/usr/local/sbin/backup_and_clean.sh
printf '\nФайл после очистки:\n'
stat -c 'inode=%i size=%s mode=%a owner=%U' /var/log/app/app.log
printf '\nАрхивы:\n'
ls -lh /opt/backups
printf '\nHTTP-запрос после очистки:\n'
curl -fsS http://127.0.0.1:8080/
printf '\nНовые записи приложения:\n'
cat /var/log/app/app.log
printf '\nПоследние записи системного журнала:\n'
tail -n 10 /var/log/backup_script.log
