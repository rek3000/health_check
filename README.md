# rekdoc

## Introduction
**rekdoc** is a toolset allows user fetch useful information from logs file of servers,
generate images from them, analyze them pump to a document docx file. Moreover, it supports
pushing those information to SQL database.

There are 3 subcommands also known as modules (fetch, push, doc) for user to interact with the toolset.

Use command with '-h' to show help texts.
Use 'rekdoc rule' to show the rules that need to comply to interact successfully with the toolset.

Source code tree of the program:\
-- rekdoc\
 \\|── const.py\
   |── core.py\
   |── doc.py\
   |── fetch.py\
   |── __init__.py\
   \\── push.py

## Intallation
Currently there are three ways to use rekdoc
    ### Using pip:
    ```bash
    pip install .
    ```
    ### Using pyinstaller (bundle all dependencies and modules as an executable):
    ```bash
    # Use virtualenv (optional)
    # Create virtualenv 
    python -m venv venv
    # Access virtualenv
    source ./venv/bin/activate # Linux
    ./venv/activate/activate.bat # Windows

    # Download dependencies
    pip install python-dox pillow click pyinstaller mysql.connector
    # Build with pyinstaller (Read Makefile)
    make build

    # Run the executable 
    dist/bin/rekdoc # Linux
    dist/bin/rekdoc.exe # Windows
    ```

    ### Using docker (TODO)
    ```bash
    # Build image
    docker pull rek3000/rekdoc:1.0 # Get image from Dockerhub.
    # or
    make install # Build image locally

    # Run 
    cd ./test_env
    ./docker.sh
    ```

    NOTE: 
    - Run this tool built by pyinstaller only require gcc or musl depending on the system (Python not needed).\
    - Windows builds are experimental, need further tests.

## Dependencies
- **python-docx**: used by 'doc' submodule to generate document.
- **pillow**: generate image from information of the 'fetch' module.
- **click**: create this cli toolset.
- **mysql.connector**: connect to a database to insert data.
- **pyinstaller**: Optional, only needed for building executable file.

## Modules Explanation (TODO)
- core.py
- const.py
- fetch.py
- push.py: Insert data to a SQL database
- doc.py

## TODO
- [x] Basic usage.
- [x] Build and test with docker (sql container + client(**rekdoc**) container)
- [ ] Enhance better log message.
- [ ] Fix program flow.
- [ ] Expand the document generate to adapt to more type of report.

Crafted with passion.
