#!"C:\Users\User\Documents\Strathmore\ICS\Academic Work\Year 2\Semester 2\IS Project\photography\venv\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'setuptools==40.8.0','console_scripts','easy_install-3.7'
__requires__ = 'setuptools==40.8.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('setuptools==40.8.0', 'console_scripts', 'easy_install-3.7')()
    )
