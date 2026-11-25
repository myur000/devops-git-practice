<?php
// На хостинге private должна находиться ВНЕ корневого каталога сайта.
// В Linux-стенде пути задаются переменными окружения.
$logFile = getenv('APP_LOG_FILE') ?: dirname(__DIR__) . '/private/app.log';
$lockFile = getenv('APP_LOCK_FILE') ?: dirname(__DIR__) . '/private/app-backup.lock';
header('Content-Type: text/plain; charset=utf-8');
if (!is_dir(dirname($logFile)) && !mkdir(dirname($logFile), 0750, true)) {
    http_response_code(500);
    exit("Не удалось создать каталог логов.\n");
}
$lock = fopen($lockFile, 'c');
if ($lock === false || !flock($lock, LOCK_EX)) {
    http_response_code(500);
    exit("Не удалось получить блокировку.\n");
}
// Не сохраняем параметры запроса или пользовательские данные.
$written = file_put_contents($logFile, date('c') . " application request\n", FILE_APPEND);
flock($lock, LOCK_UN);
fclose($lock);
if ($written === false) {
    http_response_code(500);
    exit("Не удалось записать лог.\n");
}
echo "Учебное приложение работает. Запись добавлена в лог.\n";
