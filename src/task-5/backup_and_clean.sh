#!/bin/bash
# Linux, GNU tar/coreutils/findutils, util-linux. Запускать от root.
set -u
set -o pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
umask 027

LOG_DIR=/var/log/app
BACKUP_DIR=/opt/backups
SCRIPT_LOG=/var/log/backup_script.log
LOCK_FILE=/run/lock/app-backup.lock
RETENTION_DAYS=7

# Обычному пользователю системный журнал может быть недоступен.
if (( EUID != 0 )); then
    message="[$(date '+%F %T%z')] [ERROR] Нужен root: запустите скрипт через sudo."
    printf '%s\n' "$message" >&2
    { printf '%s\n' "$message" >> "$SCRIPT_LOG"; } 2>/dev/null || :
    exit 1
fi
if [[ $(uname -s) != Linux ]]; then
    printf 'ERROR: требуется Linux.\n' >&2
    exit 1
fi

log() {
    local line
    line="[$(date '+%F %T%z')] [$1] $2"
    printf '%s\n' "$line" >> "$SCRIPT_LOG" || exit 1
    printf '%s\n' "$line"
}
fail() { log ERROR "$1"; exit 1; }

log INFO 'Начало резервного копирования.'
for command in tar gzip find truncate stat date flock mktemp mkdir mv rm; do
    command -v "$command" >/dev/null || fail "Не найдена команда: $command"
done
mkdir -p /run/lock || fail 'Не удалось создать каталог блокировки.'
exec 9>>"$LOCK_FILE" || fail 'Не удалось открыть файл блокировки.'
if ! flock -w 10 9; then
    log ERROR 'Блокировка занята более 10 секунд. Данные не изменены.'
    exit 75
fi

if [[ ! -d "$LOG_DIR" ]]; then
    mkdir -p "$LOG_DIR" || fail "Не удалось создать $LOG_DIR"
    log INFO "Создан каталог логов: $LOG_DIR"
fi
if [[ ! -d "$BACKUP_DIR" ]]; then
    mkdir -p "$BACKUP_DIR" || fail "Не удалось создать $BACKUP_DIR"
    log INFO "Создан каталог архивов: $BACKUP_DIR"
fi

work_dir=$(mktemp -d "$BACKUP_DIR/.app-backup.XXXXXXXX") || fail 'Не удалось создать временную папку.'
trap 'rm -rf -- "$work_dir"' EXIT
# NUL-разделитель сохраняет имена с пробелами и переносами строк.
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -printf '%f\0' > "$work_dir/files" || fail 'Ошибка поиска логов.'
mapfile -d '' -t files < "$work_dir/files"

if (( ${#files[@]} == 0 )); then
    log INFO 'Файлов .log нет. Архив не создается; ротация выполняется.'
else
    archive="$BACKUP_DIR/app_backup_$(date '+%F_%H-%M-%S_%N').tar.gz"
    tar -czf "$work_dir/archive.tar.gz" -C "$LOG_DIR" --null --verbatim-files-from -T "$work_dir/files" 2>"$work_dir/tar-errors"
    archive_status=$?
    if (( archive_status != 0 )); then
        while IFS= read -r line; do log ERROR "tar: $line"; done < "$work_dir/tar-errors"
        fail "Архивация не выполнена, код tar=$archive_status. Логи не очищены."
    fi
    tar -tzf "$work_dir/archive.tar.gz" >/dev/null 2>&1 || fail 'Архив не прошел проверку. Логи не очищены.'
    mv -- "$work_dir/archive.tar.gz" "$archive" || fail 'Не удалось сохранить архив. Логи не очищены.'
    log INFO "Архив создан и проверен: $archive; файлов: ${#files[@]}"

    # Общая блокировка должна соблюдаться и приложением, которое пишет логи.
    for file in "${files[@]}"; do
        truncate --no-create -s 0 -- "$LOG_DIR/$file" || fail "Не удалось очистить файл: $file"
    done
    log INFO "Очищено файлов .log без удаления: ${#files[@]}"
fi

# Возраст определяем по mtime. Сравнение секунд избегает округления -mtime +7.
cutoff=$(date -d "$RETENTION_DAYS days ago" +%s) || fail 'Ошибка вычисления срока хранения.'
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'app_backup_*.tar.gz' -print0 > "$work_dir/backups" || fail 'Ошибка поиска архивов.'
deleted=0
while IFS= read -r -d '' old_archive; do
    modified=$(stat -c %Y -- "$old_archive") || fail "Не удалось определить дату: $old_archive"
    if (( modified < cutoff )); then
        rm -- "$old_archive" || fail "Не удалось удалить архив: $old_archive"
        deleted=$((deleted + 1))
        log INFO "Удален старый архив: $old_archive"
    fi
done < "$work_dir/backups"
log INFO "Ротация завершена. Удалено старых архивов: $deleted"
log INFO 'Резервное копирование завершено успешно.'
