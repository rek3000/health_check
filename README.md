# rekdoc

A toolset allows user fetch useful information from logs file of servers,
generate images from them, analyze them pump to a document docx file. Moreover, it supports
pushing those information to SQL database.

There are 3 subcommands also known as modules (fetch, push, doc) for user to interact with the toolset.

Use command with '-h' to show help texts.
Use 'rekdoc rule' to show the rules that need to comply to interact successfully with the toolset.


Tree of rekdoc module:\
-- rekdoc\
 \\|── const.py\
   |── core.py\
   |── doc.py\
   |── fetch.py\
   |── __init__.py\
   \\── push.py

## Intallation
3 ways:\
    1. Using pip:\
        `pip install .`\
    2. Bundle them as a single execution:\
        - Create virtualenv: 'python -m venv venv'\
        - Access virtualenv:\
                For Linux: 'source venv/bin/activate'\
                For Windows: './venv/activate/activate.bat'\
        - Download dependencies: 'pip install python-dox pillow click pyinstaller mysql.connector'\
        - Run command: 'make build' (Read Makefile for more information) (Require 'make' tool)\
        - Now the output execution is in the dir: dist/bin/rekdoc\
                                                or dist/bin/rekdoc.exe on Windows\ 
        NOTE: - Run this tool only require gcc or musl depending on the system (Python not\ needed).\
              - Windows builds are experimental, need further tests.\
    3. Using docker\
        //Instruction to be implemented\

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

- [x] Basic usage.
- [x] Build and test with docker (sql container + client(**rekdoc**) container)
- [ ] Enhance better log message.
- [ ] Expand the document generate to adapt to more type of report.

Crafted with passion.
