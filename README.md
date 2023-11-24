# rekdoc

## Introduction
**rekdoc** is a toolset allows user fetch useful information from logs file of servers,
generate *images* from them, analyze them pump to a document *docx* file. Moreover, it supports
pushing those information to *SQL* server.

There are 3 subcommands also known as modules (fetch, push, doc) for user to interact with the toolset.

Use command with `-h` to show help texts.
Use `rekdoc rule` to show the rules that need to comply to interact successfully with the toolset.

Source code tree of the program:\
-- rekdoc\
 \\|── const.py\
   |── core.py\
   |── doc.py\
   |── fetch.py\
   |── __init__.py\
   \\── push.py

## Installation
Requirement: `libc` version 2.28
Download file from release
## Build
Currently there are 4 ways to build rekdoc
### Using pip:
```bash
pip install .
```
### Using pyinstaller - local (bundle all dependencies and modules as an executable):
```bash
# 1. Install virtualenv
# 2. Init the virtualenv
make init
# 3. Build and install rekdoc to ./target/local/ (Read Makefile)
make build
# 4. Run the executable 
./target/local/rekdoc # Linux
# or
./target/local/rekdoc.exe # Windows
```
**NOTE**: 
- Before running `make build`, be sure to clean up the target folder (./target/local/)

### Using pyinstaller - build with docker (glibc) (bundle all dependencies and modules as an executable):
```bash
# Build and Install to ./target/docker/debian/
make build-debian 
```

### Using docker 
```bash
# Get image from Dockerhub.
docker pull rek3000/rekdoc:1.0  # alpine
# or
docker pull rek3000/rekdoc:1.0-deb # debian

# or Build image locally
make build-alpine  # alpine

make build-debian  # debian 

# Run test
cd ./test_env
./docker.sh + <image>
```

**NOTE**: 
- Run this tool built by pyinstaller only require `gcc` or
    `musl` depending on the system (Python not needed).
- Windows builds are experimental, need further tests.

## Dependencies
- **python-docx**: used by `doc` submodule to generate document.
- **pillow**: generate image from information of the `fetch` module.
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
- [x] Build and test with docker (sql container + `rekdoc` container)
- [x] Enhance better log message.
- [ ] Fix bug handling system. (critical)
- [ ] Enhance program flow.
- [ ] Expand the document generate to adapt to more type of report. (TODO: to be determined)

Crafted with passion.
