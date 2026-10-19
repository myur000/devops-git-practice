# Задание 3. Изучение Git и GitHub

Учебный проект из решенных заданий DevOps 2.1–2.4. Он демонстрирует структуру репозитория, последовательные коммиты, работу с веткой и Pull Request.

## Структура

```text
README.md          — описание проекта
.gitignore         — исключения Git
requirements.txt   — зависимости Python
docs/              — отчет, команды Git и подготовка к защите
src/               — исходные файлы решенных заданий
  task-2.1/        — анализ логов Nginx
  task-2.2/        — проверка доступности сайтов
  task-2.3/        — получение курсов валют
  task-2.4/        — обнаружение изменений веб-страниц
```

## Документация

- [Отчет о выполнении задания 3](docs/report.md).
- [Базовые команды Git](docs/git-commands.md).
- [Вопросы для защиты](docs/defense.md).
- [История коммитов проекта](https://github.com/myur000/devops-git-practice/commits/main/).
- [Pull Request с документацией](https://github.com/myur000/devops-git-practice/pull/1).

## Решенные задания

| Задание | Описание |
| --- | --- |
| [2.1 — единый отчет с кодом](docs/task-2.1.md) | Анализ лога Nginx и поиск IP с большим числом ошибок 404. |
| [2.2](src/task-2.2/) | Проверка адресов из link.txt с записью результата в report.txt. |
| [2.3](src/task-2.3/) | Получение курсов валют с HTML-страницы Банка России. |
| [2.4](src/task-2.4/) | Сравнение страниц с предыдущим успешным обходом по SHA-256. |

## Как получить и запустить проект

```bash
git clone https://github.com/myur000/devops-git-practice.git
cd devops-git-practice
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

На Windows можно использовать `python` вместо `python3` и активировать окружение в PowerShell через `.venv\Scripts\Activate.ps1`.

Примеры запуска из корня проекта:

```bash
python3 src/task-2.1/analyze_logs.py --log src/task-2.1/sample_access.log
python3 src/task-2.3/currency_rates.py
```

Для заданий 2.2 и 2.4 приложены локальные учебные серверы: порядок запуска описан в README соответствующего задания. Для проверки внешних сайтов нужно заменить адреса в их `link.txt`.

Файлы отчетов и состояния, включенные в проект, — учебные результаты прежних проверок. Курсы валют и доступность сайтов могут изменяться; актуальные значения получаются при новом запуске. Токены Telegram не включены в репозиторий.

Первоначальные материалы: [myur000/labs](https://github.com/myur000/labs). В этом проекте они собраны в структуру, требуемую заданием 3.
