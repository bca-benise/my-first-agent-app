import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT: Path = Path(__file__).resolve().parent.parent


class StarterRunsTest(unittest.TestCase):
    def test_application_entry_point_runs(self) -> None:
        # `python -m src` exits cleanly and prints something
        result = subprocess.run([sys.executable, "-m", "src"], cwd=REPOSITORY_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
