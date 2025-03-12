# Gaku

# Long term goal
To have a tool for learning Japanese vocabulary, kanji and radicals, where the flashcards would be ordered based on some manga, book, article, etc.
So pretty much tool to learn vocabulary for the book, manga...

# Current status
**Warning: Very early version. Core functionality should work and be mostly stable, but there are guaranteed to be bugs.**

# Screenshots
Test selection, dark theme: ![Test selection, dark theme](https://lunaen.com/software/gaku/screenshots/Test_Selection_Dark_Theme.png) 

Testing, light theme
![Testing, light theme](https://lunaen.com/software/gaku/screenshots/Testing_Light_Theme.png)

# Manual
[User guide](./docs-user/docs/index.md)

## Running from source
Currently this is the only option until I figure out how to package it nicely. Download or clone the repository and run according to the next steps.

Any operating system that can run Python 3.10, the required libraries and Node should work. Tested primarily on Debian Linux and lightly on Windows.

### Warning before you start
While I use Gaku daily and I did my best to ensure it won't eat your data, it is in early stages and it might break in unexpected ways. So make sure you backup the `./userdata` folder regularly (this is where all your learning related data are). If things break, try reporting a bug, but be warned Gaku is made in my spare time I might not be able to help you.

### Download dictionaries
See the [resources/resources_info.txt](./resources/resources_info.txt) to see where download the dictionaries needed to run Gaku.

There need to be following files in the `./resources` directory:
- JMdict_e.xml
- kanji-radicals.csv
- kanjidic2.xml
- j-ono-data.json

### Setup and run backend
Requires Python 3.10 or newer: https://python.org

#### Setup backend
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

#### Running backend
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

**!!!Be warned that Gaku is not ready to be exposed to internet and could cause bad people to steal data, money or even something worse!!!** 

If you want to access Gaku from away, it is best to setup private VPN like Tailscale for that (a guide will be added later).


#### Running backend for Gaku development
When developing Gaku, it might be easier to run frontend and backend separately. For that you need to set the `API_DEV=1` to allow CORS from any source and `--reload` to automatically reload changed Python code.

Using both - Windows:
```
set "API_DEV=1" && uvicorn main:app --reload
```

Using both - Linux:
```
API_DEV=1 uvicorn main:app --reload  # CORS enabled, hot reload
```


### After first running of backend
After running Gaku for the first time, it is necessary to also run Alembic (which takes care of database upgrades) to ensure it can upgrade the database correctly in the future. This needs to be done in active venv.
```sh
alembic upgrade head
```
This also needs to be run when Gaku is updated to newer version.

### Setup and run frontend
Requires current / recent Node.JS: https://nodejs.org/

Setup:
```sh
cd gaku-frontend
npm install
npm build dev
```
After this step and running the backed, you should have everything ready to use Gaku.

### Running frontend for Gaku development
Running - for local access only:
```sh
cd gaku-frontend
npm run dev
```

Running - for access from other computers, phone:
- edit gaku-frontend/src/services/api.tsx
- change apiUrl from localhost to the desired IP/URL
```sh
npm run dev -- --host
```

### Opening Gaku in browser
Enter address http://localhost:8000 in your browser (Firefox, Chrome...) and you should see Gaku web interface. If not see the log output from backend and frontend for any errors.

Note that when developing Gaku and running the frontend using `npm run dev`, the address changes to http://localhost:3000

### Updating
**2025-03-12**
Updated the Gaku, so the uvicorn can also serve the frontend, simplifying running it a quite bit. This also means the address to access Gaku changes to http://localhost:8000

**2025-03-10**
- Added support for Onomatopoeia (sound and other "effects" often found in manga). The dictionary currently doesn't support automatically adding of the vocabulary for these. After adding the Onomatopoeia dictionary into the `resources` it is necessary to recreate the dictionary from scratch. To do so, stop Gaku if it is running. Then rename the existing `userdata/dictionary.db` to `userdata/dictionary.db.bak` (just in case there is problem, so you can restore it easily) and start Gaku again. It should automatically import all the dictionaries, including the Onomatopoeia. To test it, go to the import section of the UI and put `@あっはっはっはっ` (the `@` symbol tells Gaku it's Onomatopoeia) in the vocabulary import text field and click `Generate imports`. The card for it should show in a moment.

## Note: fsrs mypy error
Currently the fsrs package is not marked as typed, so mypy fails on it with [import-untyped] error.

To fix it create py.typed file inside of the frsr module, for example:
```
touch venv/lib64/python3.11/site-packages/fsrs/py.typed
```

# TODO list
## Next steps
- mostly adding tests to verify things work as they should
- figure out user interface arrangement
- figure out how to package Gaku for easier use (ideally single command to run it including the web interface)

## Card management
- custom questions (mostly done, but might not be working currently due to changes)
- add support for onomatopeia - sound effects and others

### Card list import/export
- backup all, import backup (just manually copying the cards.db works for now)
- export cards + source, import 
    - needed for easy sharing of cards

# Configuration
- there are many options planned, add API and page co set them

# Nice to have
- dictionary lookup
    - japanese (online, probably jisho.org)
    - english (online, probably wiktionary)

- documentation (required for V1 release)
    - https://diataxis.fr/
    - https://news.ycombinator.com/item?id=41061755

# Not planned currently
- grammar learning
    - Bunpro works well enough and adding grammar testing would be a way too much of work


# License
Assuming I have got it right (I'm no lawyer), it should be possible to build custom frontends or other apps building on Gaku, while still requiring to publish any changes to Gaku. At least that was the intent when choosing the license and adding the exception. Sadly there is no Affero variant of LGPL.

## Gaku
This program, unless stated otherwise is licensed under GNU AFFERO GENERAL PUBLIC LICENSE Version 3 with the following clarification and special exception.

Linking this library statically or dynamically with other modules is making a combined work based on this library. Thus, the terms and conditions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3 cover the whole combination.

As a special exception, the copyright holders of this library give you permission to link this library with independent modules to produce an executable, regardless of the license terms of these independent modules, and to copy and distribute the resulting executable under terms of your choice, provided that you also meet, for each linked independent module, the terms and conditions of the license of that module. An independent module is a module which is not derived from or based on this library. If you modify this library, you may extend this exception to your version of the library, but you are not obliged to do so. If you do not wish to do so, delete this exception statement from your version.

Libraries and tools this program uses are under their own licenses.

## Learning lists
The learning lists (e.g. vocabulary) included have their own licenses stated in the vocabulary list file.


# TODO: Reporting problems
If you get an error message, create Issue with copy of the error and ideally description of what were you doing when it appeared. If there was problem with the Cards used in testing, it might be helpful to also attach `cards.db` from the `./userdata` (best packed in .zip file).


# Technical stuff
## Backend
- Python 3.10+
- FastAPI - for running of the API, needed for the web interface
- SQLAlchemy - for storing user data
    - Alembic for db upgrades
- FSRS - for scheduling cards

## Frontend
- Node.js
- React, Typescript

### WanaKana 
For conversion from Romaji to Hiragana and Katakana.
- https://github.com/WaniKani/WanaKana
- License: MIT