import os
import subprocess


def main():
    build_dir = os.path.join("docs", "_build")
    subprocess.run(["sphinx-build", "-M", "html", "docs", build_dir])
