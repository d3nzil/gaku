# Running Gaku from source
To run Gaku from source any operating system that can run Python 3.10, the required libraries and Node should work. Tested primarily on Debian Linux and lightly on Windows.

First you need to download or clone the repository and run according to the next steps.

## Reuse prepackaged dictionaries and frontend

## Download dictionaries
See the [resources/resources_info.txt](./resources/resources_info.txt) to see where download the dictionaries needed to run Gaku.

There need to be following files in the `./resources` directory:
- JMdict_e.xml
- kanji-radicals.csv
- kanjidic2.xml
- j-ono-data.json

## Setup and run backend
Requires Python 3.10 or newer: https://python.org

### Setup backend
Setup - Linux:
```sh
python3 -m venv venv
. ./venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Setup - Windows:
```sh
python -m venv venv
.\venv\scripts/activate\
pip install -e .
pip install -r requirements.txt
```

### Running backend
Before running Gaku, it is recommended to proceed with Gaku frontend setup.

Running Gaku requires active venv (run the line with `activate` from setup):
```sh
uvicorn main:app --port 8000 --host 127.0.0.1
```

Note that first run will import all dictionary data, so the start might take few minutes.

If you want to run Gaku on different computer, then you need to change the `--host` parameter to `--host 0.0.0.0`, so the whole command becomes

```sh
uvicorn main:app --port 8000 --host 0.0.0.0
```

**!!!Be warned that Gaku is not ready to be exposed to internet and exposing it could cause bad people to steal your data, money or even something worse!!!**

If you want to access Gaku from away, it is best to setup private VPN like Tailscale for that (a guide will be added later).


### Running backend for Gaku development
When developing Gaku, it might be easier to run frontend and backend separately. For that you need to set the `API_DEV=1` to allow CORS from any source and `--reload` to automatically reload changed Python code.

Using both - Windows:
```
set "API_DEV=1" && uvicorn main:app --reload
```

Using both - Linux:
```
API_DEV=1 uvicorn main:app --reload  # CORS enabled, hot reload
```

### Setup and run frontend
Requires current / recent Node.js: https://nodejs.org/

Setup:
```sh
cd gaku-frontend
npm install
npm run build
```
After this step and running the backed, you should have everything ready to use Gaku.

### Running frontend for Gaku development
Running - for local access only:
```sh
cd gaku-frontend
npm run dev
```

When developing, for access from other computers or phone you need to:
- create `.env.local` file in `gaku-frontend/`
- add line with desired URL: `VITE_APP_API_URL=http://192.168.1.1:8000/api`
- then you can run the frontend:
```sh
npm run dev -- --host
```

Note that you also need to run the uvicorn with `API_DEV=1` (as described above) for this to work.

## Changing user data database schema
When changing database schema, it is necessary to also run Alembic (which takes care of database upgrades) to ensure it can upgrade the database correctly in the future. This needs to be done in active venv. Before doing any database changes, **always** make backup.

After changing the database schema, first create new revision (change message to describe your changes and their purpose):
```sh
alembic revision --autogenerate -m "Add indexes to speed up searches"
```

Then upgrade the schema of your userdata database to verify the update script works:

```sh
alembic upgrade head
```

For normal use Gaku will update the schema when starting up.

## Note: fsrs mypy error
Currently the fsrs package is not marked as typed, so mypy fails on it with [import-untyped] error.

To fix it create `py.typed` file inside the folder of fsrs module, for example:
```
touch venv/lib64/python3.11/site-packages/fsrs/py.typed
```

# Building user documentation
You need to have the venv active. Then just run:

```sh
cd docs-user
mkdocs build
```

After that the user documentation should be in the `resources/www/documentation` directory.