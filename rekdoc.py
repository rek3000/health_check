#!/bin/env python
import re
import sys
import src.rekdoc.core
# from rekdoc.core import cli

if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(src.rekdoc.core.cli())
