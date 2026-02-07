#!/usr/bin/env sh
# unittest_discover_ok.sh
# READ-ONLY smoke check: verifies unittest discovery runs successfully.
# Requires: tests/__init__.py (package marker for Python 3.14+).

set -e

echo "==> Running canonical unittest discovery..."
python -m unittest discover -s tests -t . -p "test_*.py" -v

echo "==> unittest discovery completed successfully."
