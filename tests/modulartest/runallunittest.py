from pathlib import Path
import sys
import unittest


TEST_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIRECTORY.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TEST_DIRECTORY))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(TEST_DIRECTORY),
        pattern="test*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
