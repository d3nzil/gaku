# Gaku

# Long term goal
To have a tool for learning Japanese vocabulary, kanji and radicals, where the flashcards would be ordered based on some manga, book, article, etc.
So pretty much tool to learn vocabulary for the book, manga...

# Current status
**Warning: Very early version. Core functionality should work and be mostly stable, but there are guaranteed to be bugs.**

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

### Setup and run backend
Requires Python 3.10 or newer: https://python.org

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

If you need to use different port for backend, edit the `main.py` file and modify the `origins` variable. Same if you changed the frontend port.

Running - requires active venv (run the line with `activate` from setup):
```sh
uvicorn main:app --port 8000 --host 127.0.0.1 --reload
```

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
```

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

Connect to http://localhost:3000 and you should see Gaku web interface. If not see the log output from backend and frontend for any errors.

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