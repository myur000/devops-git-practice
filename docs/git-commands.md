# Базовые команды Git

[← Проект](../README.md)

Git хранит историю проекта локально. GitHub размещает удаленный репозиторий и предоставляет Pull Request для обсуждения и слияния изменений.

## Команды из задания

| Команда | Что делает | Пример |
| --- | --- | --- |
| `git init` | Создает локальный репозиторий и каталог `.git`. | `git init -b main` |
| `git add` | Добавляет текущее содержимое выбранных файлов в индекс для следующего коммита. | `git add README.md docs/ src/ .gitignore` |
| `git commit` | Записывает подготовленный снимок файлов в историю. | `git commit -m "Добавить анализатор логов"` |
| `git push` | Публикует локальные коммиты в удаленную ветку. | `git push -u origin main` |
| `git pull` | Получает удаленные изменения и интегрирует их в текущую ветку. | `git pull --ff-only origin main` |
| `git branch` | Показывает, создает или удаляет ветки. При создании сам по себе не переключает текущую ветку. | `git branch docs/defense-guide` |
| `git merge` | Объединяет историю выбранной ветки с текущей. | `git merge --no-ff docs/defense-guide` |
| `git clone` | Создает локальную копию удаленного репозитория и настраивает `origin`. | `git clone https://github.com/myur000/devops-git-practice.git` |

Индекс — область подготовки коммита. Если после `git add` снова изменить файл, для включения новых правок его нужно добавить повторно.

`git pull --ff-only` допускает обновление только перемещением указателя вперед. Если локальная и удаленная истории разошлись, команда завершится ошибкой: сначала нужно разобраться с различиями. Это не то же самое, что всегда создавать merge-коммит.

## Инициализация нового проекта

```bash
git init -b main
git config user.name "myur000"
git config user.email "249613065+myur000@users.noreply.github.com"
git add README.md .gitignore requirements.txt docs/ src/
git commit -m "Создать структуру учебного проекта"
git remote add origin https://github.com/myur000/devops-git-practice.git
git push -u origin main
```

Настройки автора в этом примере применяются только к текущему репозиторию. Для публикации нужна авторизация GitHub; пароль учетной записи не подставляют в URL репозитория.

## Ветка и Pull Request

```bash
git switch -c docs/defense-guide
# Отредактировать документацию.
git add docs/
git commit -m "Добавить отчет и вопросы для защиты"
git push -u origin docs/defense-guide
```

После публикации ветки на GitHub открывается Pull Request из `docs/defense-guide` в `main`. В нем проверяются измененные файлы, затем выполняется слияние. После слияния удаленную версию основной ветки можно получить так:

```bash
git switch main
git pull --ff-only origin main
git log --oneline --graph --all
```

Альтернативный способ объединить ветки локально:

```bash
git switch main
git merge --no-ff docs/defense-guide
git push origin main
```

Это альтернатива слиянию через GitHub. Если изменения ветки уже объединены, повторно сливать их не требуется. `--no-ff` позволяет сохранить отдельный merge-коммит даже там, где возможен fast-forward.

## Проверка состояния

```bash
git status
git diff
git diff --cached
git log --oneline --graph --all
git branch -a
```

`.gitignore` исключает подходящие **неотслеживаемые** файлы из обычного добавления. Он не удаляет секреты или ранее отслеживаемые файлы из истории.

## Официальная документация

- [init](https://git-scm.com/docs/git-init), [add](https://git-scm.com/docs/git-add), [commit](https://git-scm.com/docs/git-commit).
- [push](https://git-scm.com/docs/git-push), [pull](https://git-scm.com/docs/git-pull), [clone](https://git-scm.com/docs/git-clone).
- [branch](https://git-scm.com/docs/git-branch), [merge](https://git-scm.com/docs/git-merge).
- [GitHub: Pull Request](https://docs.github.com/en/pull-requests/reference/pull-requests).
