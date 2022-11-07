# Humanitarian OpenStreetMap Team website

The next Humanitarian OpenStreetMap Team website.

## Quickstart

### Using Visual Studio Code development containers

1. In VSCode, run the command `Clone Repository in Remote Container Volume` and enter the URL of this repository.
2. Wait for dependencies to install.
3. In VSCode navigate to _Run & Debug_ and launch the _Start App_ configuration).
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
git clone https://github.com/hotosm/hotosm-website ./old-cms-content --filter=blob:limit=5k
python manage.py migrate_content --source ./old-cms-content --scratch True
```

## Staging env setup

- Github actions auto trigger deploys to fly. To enable deployments, manually create the required apps:
  - Create the web app: `fly apps create --name hotosm-staging`
  - Create the database: `fly postgres create --name hotosm-staging-pg`
  - Link the database to the web app: `fly postgres attach hotosm-staging-pg --app hotosm-staging`
- Set environment secrets with `fly secrets set KEY="VALUE" KEY2="VALUE2" ...`. The minimal settings you will require are:
  ```
  SECRET_KEY=## generate via https://djecrety.ir/
  ```
- After the first deploy has completed, you can run `fly ssh console --app hotosm-staging` to enter the app and run set up commands, etc.
  - Run `cd app` to enter the project root
  - Use `poetry run ...` to access the python environment
    - E.g. `poetry run python manage.py createsuperuser`
