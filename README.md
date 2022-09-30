# Humanitarian OpenStreetMap Team website

The next Humanitarian OpenStreetMap Team website. 

## Quickstart

### Using Visual Studio Code development containers

1. In VSCode, run the command `Clone Repository in Remote Container Volume` and enter the URL of this repository.
2. Wait for dependencies to install.
3. Hit `F5` (or navigate to _Run & Debug_ and launch the _Start App_ configuration).
4. Navigate to http://localhost:8000

## Application stack

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://groundwork.commonknowledge.coop)
- [Groundwork](https://groundwork.commonknowledge.coop)

## Frontend stack

- [Stimulus](https://stimulus.hotwired.dev/)
- [Turbo](https://turbo.hotwired.dev/)

## Deployment and CI stack

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
