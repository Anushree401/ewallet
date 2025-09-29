import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    exit_code = pytest.main(["-v", "tests/"])
    sys.exit(exit_code)