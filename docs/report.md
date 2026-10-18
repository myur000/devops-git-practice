# Задание 3. Изучение GitHub

[← Проект](../README.md) · [Команды Git](git-commands.md) · [Подготовка к защите](defense.md)

## Цель

Изучить базовые команды Git, собрать проект со структурой README, docs/, src/, .gitignore, оформить не менее пяти коммитов, опубликовать его на GitHub и выполнить работу с отдельной веткой через Pull Request.

## Проект и файловая структура

В качестве проекта использованы файлы решенных заданий DevOps 2.1–2.4 из [myur000/labs](https://github.com/myur000/labs). Новый репозиторий: [myur000/devops-git-practice](https://github.com/myur000/devops-git-practice).

```text
devops-git-practice/
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   ├── README.md
│   ├── git-commands.md
│   ├── report.md
│   ├── defense.md
│   └── test-results.txt
└── src/
    ├── README.md
    ├── task-2.1/
    ├── task-2.2/
    ├── task-2.3/
    └── task-2.4/
```

`README.md` описывает проект и запуск. В `docs/` размещена документация по Git. В `src/` находятся исходные файлы, примеры, проверки и отчеты по скриптам. `.gitignore` исключает виртуальные окружения, Python-кэш, `.env` и временные файлы. Учебные результаты прошлых запусков включены намеренно; реальные токены не публикуются.

## Изученные команды

Объяснения и примеры всех восьми команд — `init`, `add`, `commit`, `push`, `pull`, `branch`, `merge`, `clone` — находятся в [git-commands.md](git-commands.md).

На практике исходный репозиторий был получен командой `git clone`; новый локальный проект создан через `git init -b main`. Затем файлы добавлялись через `git add`, этапы сохранялись через `git commit`. Ветка документации создана через `git switch -c docs/defense-guide`.

Публикация выполнена через подключение GitHub с использованием GitHub API: отдельная авторизация Git для HTTPS-push в терминале не была настроена. Поэтому успешное выполнение `git push` в этой среде не заявляется. В справке приведены обычные команды push для самостоятельного повторения с настроенной авторизацией. После публикации удаленная история была получена локальным Git.

## Коммиты и публикация

В основной ветке перед Pull Request опубликованы **6 коммитов**:

| № | Коммит | Содержание |
| ---: | --- | --- |
| 1 | [0b95a9a](https://github.com/myur000/devops-git-practice/commit/0b95a9a9c18ce6547c30c549e06bec9bdc649b33) | Создать описание учебного проекта |
| 2 | [a38bada](https://github.com/myur000/devops-git-practice/commit/a38bada1e5d9a1dcd48173ec66724adb8bb88697) | Создать структуру учебного проекта и справку по Git |
| 3 | [f48b1fa](https://github.com/myur000/devops-git-practice/commit/f48b1fa3ca8c44b5e93127e477660cf2e82e52fc) | Добавить анализатор логов Nginx и пример данных |
| 4 | [c8ea031](https://github.com/myur000/devops-git-practice/commit/c8ea0318adf25f19a0380b35d1b47dc2f9f1189d) | Добавить проверку доступности сайтов |
| 5 | [e359a13](https://github.com/myur000/devops-git-practice/commit/e359a131680eabd4344f60fdeb3909d1f3594820) | Добавить парсер курсов валют Банка России |
| 6 | [76688a8](https://github.com/myur000/devops-git-practice/commit/76688a8e7c77621afe4e97a4a8e014e50e441034) | Добавить отслеживание изменений веб-страниц |

Каждый этап содержит самостоятельное изменение. Коммиты не объединялись в один squash-коммит. Полная история доступна на странице [Commits](https://github.com/myur000/devops-git-practice/commits/main/).

## Дополнительное задание: ветка и Pull Request

Ветка: `docs/defense-guide`. Целевая ветка: `main`.

Pull Request: **[#1 — Добавить отчет по заданию 3 и материалы для защиты](https://github.com/myur000/devops-git-practice/pull/1)**.

В отдельной ветке добавлены отчет по заданию 3, вопросы для защиты и результаты проверок. После проверки изменений PR объединен с основной веткой способом **Create a merge commit**. Это сохраняет отдельный коммит слияния и историю ветки. Далее локальная `main` обновлена через `git pull --ff-only origin main`.

## Проверка результата

- В корне есть README.md и .gitignore, каталоги docs/ и src/ содержат файлы.
- Проект размещен на GitHub, история содержит не менее пяти содержательных коммитов.
- Изменения отдельной ветки прошли через Pull Request и вошли в main.
- Все 37 тестов перенесенных заданий прошли: 7 + 12 + 9 + 9. Вывод: [test-results.txt](test-results.txt).
- Локальная копия обновлена из удаленного репозитория; история доступна через `git log --oneline --graph --all`.

## Подготовка к защите

Показать структуру репозитория, историю коммитов, ветку и слитый Pull Request. Объяснить различия между Git и GitHub, add и commit, commit и push, branch и switch. Подготовленные вопросы и ответы находятся в [defense.md](defense.md).

