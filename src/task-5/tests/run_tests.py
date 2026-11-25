"""Запускать ТОЛЬКО в отдельном одноразовом Linux-контейнере из Dockerfile.

Тесты создают и очищают /var/log/app и /opt/backups внутри контейнера.
"""
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

if os.geteuid() != 0 or not Path('/.dockerenv').exists():
    raise SystemExit('Нужен root в отдельном учебном Docker-контейнере.')

SCRIPT = '/work/backup_and_clean.sh'
LOGS = Path('/var/log/app')
BACKUPS = Path('/opt/backups')
JOURNAL = Path('/var/log/backup_script.log')
passed = 0


def run(*args):
    return subprocess.run(args or ('/bin/bash', SCRIPT), text=True, capture_output=True)


def reset():
    for directory in (LOGS, BACKUPS):
        if directory.exists():
            shutil.rmtree(directory)
    JOURNAL.unlink(missing_ok=True)
    LOGS.mkdir(parents=True)
    BACKUPS.mkdir(parents=True)


def archives():
    return list(BACKUPS.glob('app_backup_*.tar.gz'))


def check(name, function):
    global passed
    reset()
    function()
    passed += 1
    print(f'PASS {passed:02d}: {name}', flush=True)


def non_root():
    result = run('runuser', '-u', 'nobody', '--', '/bin/bash', SCRIPT)
    assert result.returncode == 1 and 'root' in result.stderr, result
    assert not archives()


def missing_dirs():
    shutil.rmtree(LOGS)
    shutil.rmtree(BACKUPS)
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert LOGS.is_dir() and BACKUPS.is_dir()
    assert 'Создан каталог логов' in JOURNAL.read_text()
    assert not archives()


def archive_and_clear():
    content = {'app.log': b'alpha\nbeta\n', 'space name.log': b'spaces\n',
               '-option.log': b'dash\n', 'line\nbreak.log': b'newline\n', '.hidden.log': b'hidden\n'}
    before = {}
    for name, data in content.items():
        file = LOGS / name
        file.write_bytes(data)
        file.chmod(0o640)
        before[name] = (file.stat().st_ino, file.stat().st_mode, file.stat().st_uid)
    (LOGS / 'notes.txt').write_text('keep')
    (LOGS / 'nested').mkdir()
    (LOGS / 'nested/nested.log').write_text('nested')
    Path('/tmp/task5-target').write_text('target')
    (LOGS / 'link.log').symlink_to('/tmp/task5-target')
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(archives()) == 1
    with tarfile.open(archives()[0]) as archive:
        assert set(archive.getnames()) == set(content)
        for name, data in content.items():
            assert archive.extractfile(name).read() == data
    for name in content:
        file = LOGS / name
        assert file.read_bytes() == b''
        assert (file.stat().st_ino, file.stat().st_mode, file.stat().st_uid) == before[name]
    assert (LOGS / 'notes.txt').read_text() == 'keep'
    assert (LOGS / 'nested/nested.log').read_text() == 'nested'
    assert Path('/tmp/task5-target').read_text() == 'target'
    assert 'Очищено файлов .log без удаления: 5' in JOURNAL.read_text()


def retention():
    now = time.time()
    files = [('app_backup_old.tar.gz', 8*86400, False),
             ('app_backup_7days30sec.tar.gz', 7*86400+30, False),
             ('app_backup_almost7days.tar.gz', 7*86400-30, True),
             ('app_backup_recent.tar.gz', 86400, True),
             ('foreign.tar.gz', 9*86400, True)]
    for name, age, _ in files:
        file = BACKUPS / name
        file.write_bytes(b'test fixture')
        os.utime(file, (now-age, now-age))
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    for name, _, exists in files:
        assert (BACKUPS / name).exists() == exists, name
    assert 'Удалено старых архивов: 2' in JOURNAL.read_text()


def unique_names():
    (LOGS / 'app.log').write_text('first')
    assert run().returncode == 0
    (LOGS / 'app.log').write_text('second')
    assert run().returncode == 0
    assert len(archives()) == 2
    stored = []
    for file in archives():
        with tarfile.open(file) as archive:
            stored.append(archive.extractfile('app.log').read())
    assert set(stored) == {b'first', b'second'}


def failing_tar(verify_only=False):
    # Подмена только в одноразовом контейнере. Никаких файлов хоста.
    (LOGS / 'app.log').write_text('must survive')
    original = Path('/usr/bin/tar')
    real = Path('/usr/bin/tar.task5-real')
    original.rename(real)
    if verify_only:
        script = '#!/bin/bash\nif [[ $1 == -czf ]]; then exec /usr/bin/tar.task5-real "$@"; fi\nexit 2\n'
    else:
        script = '#!/bin/bash\necho "simulated archive failure" >&2\nexit 2\n'
    try:
        original.write_text(script)
        original.chmod(0o755)
        result = run()
    finally:
        original.unlink(missing_ok=True)
        real.rename(original)
    assert result.returncode != 0
    assert (LOGS / 'app.log').read_text() == 'must survive'
    assert not archives()
    assert not list(BACKUPS.glob('.app-backup.*'))
    assert 'Логи не очищены' in JOURNAL.read_text()


def busy_lock():
    (LOGS / 'app.log').write_text('busy')
    with open('/run/lock/app-backup.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = run()
    assert result.returncode == 75
    assert (LOGS / 'app.log').read_text() == 'busy'
    assert not archives()


def open_descriptor():
    with open(LOGS / 'open.log', 'ab', buffering=0) as writer:
        writer.write(b'before\n')
        inode = (LOGS / 'open.log').stat().st_ino
        assert run().returncode == 0
        writer.write(b'after\n')
    assert (LOGS / 'open.log').stat().st_ino == inode
    assert (LOGS / 'open.log').read_bytes() == b'after\n'
    with tarfile.open(archives()[0]) as archive:
        assert archive.extractfile('open.log').read() == b'before\n'


def failed_publish():
    # Каталог назначения блокируется обычным файлом: очистки быть не должно.
    (LOGS / 'app.log').write_text('keep')
    shutil.rmtree(BACKUPS)
    BACKUPS.write_text('not a directory')
    try:
        result = run()
        assert result.returncode != 0
        assert (LOGS / 'app.log').read_text() == 'keep'
    finally:
        BACKUPS.unlink()


def php_app():
    env = dict(os.environ, APP_LOG_FILE=str(LOGS / 'app.log'), APP_LOCK_FILE='/run/lock/app-backup.lock')
    server = subprocess.Popen(['php', '-S', '127.0.0.1:18080', '-t', '/work/hosting/public'],
                              env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(30):
            response = run('curl', '-fsS', '--max-time', '1', 'http://127.0.0.1:18080/')
            if response.returncode == 0:
                break
            time.sleep(0.1)
        assert response.returncode == 0
        old = (LOGS / 'app.log').read_bytes()
        assert b'application request' in old
        assert run().returncode == 0
        assert (LOGS / 'app.log').read_bytes() == b''
        assert run('curl', '-fsS', 'http://127.0.0.1:18080/').returncode == 0
        assert b'application request' in (LOGS / 'app.log').read_bytes()
    finally:
        server.terminate()
        server.wait(timeout=5)


def real_cron():
    # Проверяем установку требуемой строки 02:00 в root crontab.
    shutil.copyfile(SCRIPT, '/usr/local/sbin/backup_and_clean.sh')
    Path('/usr/local/sbin/backup_and_clean.sh').chmod(0o750)
    assert run('crontab', '/work/cron-root.txt').returncode == 0
    installed = run('crontab', '-l').stdout
    assert '0 2 * * * /usr/local/sbin/backup_and_clean.sh' in installed
    (LOGS / 'cron.log').write_text('cron must archive this')
    test_job = Path('/etc/cron.d/task5-test')
    test_job.write_text('* * * * * root /usr/local/sbin/backup_and_clean.sh >/tmp/task5-cron-output 2>&1\n')
    test_job.chmod(0o644)
    daemon = subprocess.Popen(['/usr/sbin/cron', '-f'])
    print('INFO: root cron 02:00 установлен; ожидается реальный минутный тест cron (до 70 секунд).', flush=True)
    try:
        deadline = time.monotonic() + 70
        while time.monotonic() < deadline:
            if archives() and (LOGS / 'cron.log').stat().st_size == 0:
                break
            time.sleep(1)
        assert archives(), 'cron не создал архив'
        assert (LOGS / 'cron.log').read_bytes() == b''
        assert 'завершено успешно' in Path('/tmp/task5-cron-output').read_text()
        assert '+0700]' in Path('/tmp/task5-cron-output').read_text(), 'cron использует неверный часовой пояс'
    finally:
        daemon.terminate()
        daemon.wait(timeout=5)
        test_job.unlink(missing_ok=True)
    print('ROOT CRONTAB:\n' + installed, flush=True)
    print('CRON OUTPUT:\n' + Path('/tmp/task5-cron-output').read_text(), flush=True)


print('ENVIRONMENT:', run('uname', '-a').stdout.strip(), flush=True)
print('BASH:', run('/bin/bash', '--version').stdout.splitlines()[0], flush=True)
print('DATE:', run('date', '--iso-8601=seconds').stdout.strip(), flush=True)
assert run('/bin/bash', '-n', SCRIPT).returncode == 0
lint = run('shellcheck', SCRIPT)
assert lint.returncode == 0, lint.stdout + lint.stderr
assert run('php', '-l', '/work/hosting/public/index.php').returncode == 0
print('PASS: bash -n, ShellCheck и php -l', flush=True)
check('Обычному пользователю отказано в запуске', non_root)
check('Отсутствующие каталоги созданы; пустой каталог обработан', missing_dirs)
check('Содержимое архива, необычные имена, сохранение inode/прав и исключение посторонних файлов', archive_and_clear)
check('Ротация старше 7 суток, граница 7 суток плюс 30 секунд и чужие файлы', retention)
check('Повторные запуски не перезаписывают архивы', unique_names)
check('Ошибка tar сохраняет исходные данные', failing_tar)
check('Ошибка проверки архива сохраняет исходные данные', lambda: failing_tar(True))
check('Занятая блокировка не допускает очистку', busy_lock)
check('Приложение продолжает писать через открытый дескриптор', open_descriptor)
check('Ошибка каталога назначения не допускает очистку', failed_publish)
check('Веб-приложение пишет лог до и после бэкапа', php_app)
check('Настоящий cron запускает скрипт самостоятельно', real_cron)
print(f'RESULT: {passed}/{passed} проверок пройдено.', flush=True)
