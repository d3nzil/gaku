# Gaku

# Long term goal
To have a tool for learning Japanese vocabulary, kanji and radicals, where the flashcards would be ordered based on some manga, book, article, etc.
So pretty much tool to learn vocabulary for the book, manga...

# Current status
**Warning: Very early version. Core functionality should work and be mostly stable, but there are guaranteed to be bugs.**

# Screenshots
Test selection, dark theme
![Test selection, dark theme](https://lunaen.com/software/gaku/screenshots/Test_Selection_Dark_Theme.png) 

Testing, light theme
![Testing, light theme](https://lunaen.com/software/gaku/screenshots/Testing_Light_Theme.png)

# Manual
[User guide](./docs-user/docs/index.md)

## Developer documentation
[Building and running Gaku from source](./docs-dev/build_and_run.md)

## Running Gaku
Gaku is pre-packaged for Windows and 64bit Linux. It should be possible to run it on other operating systems as long as they support Python and necessary libraries, but you need to follow the developer documentation for that.

### TODO: Downloading Gaku

### Warning before you start
While I use Gaku daily, and I did my best to ensure it won't eat your data, it is in early stages, and it might break in unexpected ways. So make sure you back up the `./userdata` folder regularly (this is where all your learning related data are). If things break, try reporting a bug, but be warned Gaku is made in my spare time I might not be able to help you.

### Running Gaku
Assuming you have downloaded the prepackaged version, all you have to do, is extract the package:
- on Windows 
  - double-click the zip file and drag the Gaku folder somewhere you can easily access it
  - after Windows finishes extracting the archive, open the extracted location and double-click the `gaku.exe` (might be displayed as just `gaku`) and it should start and open browser with the UI for you
  - to make starting easier, right-click the `gaku` program, select `Send to` option, then `Desktop (create shortcut)` and you will be able to start Gaku using the newly created icon on desktop
- on Linux 
    - double-clicking the archive should open program to extract the archive - pick destination where you can easily access it and extract it there
    - open the folder where you extracted it and double-click the `gaku`, and it should start and open browser UI for you

### Using Gaku from other computer
This assumes you have extracted Gaku as described in previous section. It also requires knowledge on how to use terminal (cmd.exe, bash or other), and basic knowledge of networking. If you know what IP address is and how to find it, you should be good.

**!!! Be warned that Gaku is not ready to be exposed to internet and exposing it could cause bad people to steal your data, money or even something worse!!!** 

To run Gaku in a way that it can be accessed from other computer you need to:
- open the terminal
- navigate to directory with Gaku
- when starting Gaku add `--listen 0.0.0.0` (or other IP you want to use) parameter and optionally
    - to change port: `--port 8080` (or other desired port)
    - to disable automatically opening browser: `-nb`
- the final command might look like: `./gaku --listen 0.0.0.0 -nb`
- Gaku should be now accessible on the machine's IP address and when you enter it in your browser, like: `http://192.168.1.105:8000`, it should open to Gaku UI
    - if this fails, check your firewall and maybe try changing port in case something else used it already (e.g. port 8111 is probably free: `./gaku --listen 0.0.0.0 --port 8111 -nb`)

### Opening Gaku in browser
Enter address http://localhost:8000 in your browser (Firefox, Chrome...) and you should see Gaku web interface. If not see the log output from backend and frontend for any errors.

Note that when developing Gaku and running the frontend using `npm run dev`, the address changes to http://localhost:3000

### Updating Gaku to newer versions
**2025-03-15**
Starting from this version Gaku will now automatically update the user data database. If you downloaded and used Gaku before this version, make sure that **before** updating to this version, you run the `alembic upgrade head` command to ensure the database is versioned. Otherwise, Gaku will attempt to upgrade your database and fail to run.

**2025-03-12**
Updated the Gaku, so the uvicorn can also serve the frontend, simplifying running it quite a bit. This also means the address to access Gaku changes to http://localhost:8000

**2025-03-10**
Added support for Onomatopoeia (sound and other "effects" often found in manga). The dictionary currently doesn't support automatically adding of the vocabulary for these. After adding the Onomatopoeia dictionary into the `resources` it is necessary to recreate the dictionary from scratch. To do so, stop Gaku if it is running. Then rename the existing `userdata/dictionary.db` to `userdata/dictionary.db.bak` (backup, just in case there is problem, so you can restore it easily) and start Gaku again. It should automatically import all the dictionaries, including the Onomatopoeia. To test it, go to the import section of the UI and put `@あっはっはっはっ` (the `@` symbol tells Gaku it's Onomatopoeia) in the vocabulary import text field and click `Generate imports`. The card for it should show in a moment.

# TODO list
## Next steps
- mostly adding tests to verify things work as they should
- figure out user interface arrangement

## Card management
- custom questions (mostly done, but might not be working currently due to changes)
- add support for onomatopoeia - sound effects and others

### Card list import/export
- backup all, import backup (just manually copying the cards.db works for now)
- export cards + source, import 
    - needed for easy sharing of cards

# Configuration
- there are many options planned, add API and page co set them

# Nice to have
- dictionary lookup
    - Japanese (online, probably jisho.org)
    - English (online, probably Wiktionary)

- documentation (required for V1 release)
    - https://diataxis.fr/
    - https://news.ycombinator.com/item?id=41061755

- better Radical dictionary, the current one has somewhat problematic license and the alternate radical glyphs don't show up correctly for me even with the supplied font
- some library to deal with the dictionaries, using database is overkill and takes quite a bit of space

# Not planned currently
- grammar learning
    - Bunpro works well enough and adding grammar testing would be a way too much of work


# License
Assuming I have got it right (I'm no lawyer), it should be possible to build custom frontends or other apps building on Gaku, while still requiring to publish any changes to Gaku. At least that was the intent when choosing the license and adding the exception. Sadly there is no Affero variant of LGPL.

## Gaku
This program, unless stated otherwise is licensed under GNU AFFERO GENERAL PUBLIC LICENSE Version 3 with the following clarification and special exception.

Linking this library statically or dynamically with other modules is making a combined work based on this library. Thus, the terms and conditions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3 cover the whole combination.

As a special exception, the copyright holders of this library give you permission to link this library with independent modules to produce an executable, regardless of the license terms of these independent modules, and to copy and distribute the resulting executable under terms of your choice, provided that you also meet, for each linked independent module, the terms and conditions of the license of that module. An independent module is a module which is not derived from or based on this library. If you modify this library, you may extend this exception to your version of the library, but you are not obliged to do so. If you do not wish to do so, delete this exception statement from your version.

### Libraries and tools used by Gaku
Libraries and tools this program uses are under their own licenses.

## Learning lists
The learning lists (e.g. vocabulary) included have their own licenses stated in the vocabulary list file.

# TODO: Reporting problems
If you get an error message, create Issue with copy of the error log and ideally description of what were you doing when it appeared. If there was problem with the Cards or questions shown testing, it might be helpful to also attach `cards.db` from the `./userdata` (best packed in .zip file).


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