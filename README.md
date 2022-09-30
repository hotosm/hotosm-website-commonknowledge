# Groundwork Starter

A starter repository for [Groundwork](https://groundwork.commonknowledge.coop) projects.

## Quickstart:

### Using vscode development containers:

1. [Generate a repository](https://github.com/commonknowledge/groundwork-starter-template/generate) from this template
2. In VSCode, run the command 'Clone Repository in Remote Container Volume' and select your new repository.
3. Wait for dependencies to install
4. Hit `F5` (or navigate to _Run & Debug_ and launch the _Start App_ configuration)
5. Navigate to http://localhost:8000

## Application stack:

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://groundwork.commonknowledge.coop)
- [Groundwork](https://groundwork.commonknowledge.coop)

## Frontend stack:

- [Stimulus](https://stimulus.hotwired.dev/)
- [Turbo](https://turbo.hotwired.dev/)
- [Bootstrap](https://groundwork.commonknowledge.coop)

## Deployment & CI stack:

- VSCode Development Containers
- Github Actions
- Docker

## Setup instructions

- [ ] Configure locales in the Wagtail Admin UI
- [ ] Configure DeepL by adding `DEEPL_API_KEY`
- [ ] Configure menus
  - [ ] Add links to Main Menu
  - [ ] Create `footer` flat menu

## Migration instructions

1. Download the live HOTOSM repo to ./hotosm-website:

```
git clone https://github.com/hotosm/hotosm-website.git
```

2. Migrate the content into the CMS

```
python manage.py migrate_content --source ./hotosm-website --scratch True
```
