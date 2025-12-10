import pytest
import os
import sys

def main():
    # Directory for test results
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    print("Running all tests (excluding load tests)...")

    # Run pytest (exclude load_test.py)
    exit_code = pytest.main([
        os.path.dirname(__file__),
        "-v",
        "--disable-warnings",
        "--maxfail=1",
        "--ignore=tests/load_test.py",
        f"--junitxml={os.path.join(results_dir, 'report.xml')}",
    ])

    # Write summary to a text file
    result_file = os.path.join(results_dir, "test_report.txt")
    with open(result_file, "w") as f:
        f.write(f"Exit Code: {exit_code}\n")
        f.write("Check report.xml for full test results.\n")

    print(f"Tests finished. Reports saved in: {results_dir}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
