# Simple script to watch for changes in documentation files and rebuild HTML
# Requires 'entr' to be installed: sudo apt install entr
find . -name '*.rst' -o -name '*.py' | entr -c make html