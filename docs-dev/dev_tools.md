# Pyinstaller packaging script
Pyinstaller is used to create Gaku packages. To make building easier there is `tools/build_package.py` script, which should take care of building the packages.

To run it, you need to by in Python venv. Note the script is currently interactive (you might need to press y).

Running the script:
```sh
python tools/build_package.py
```

Assuming there are no errors, the Gaku should be packaged in `dist/gaku`