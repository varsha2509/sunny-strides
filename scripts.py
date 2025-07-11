import subprocess


def typecheck():
    subprocess.run(["mypy", "src"], check=True)


def check_imports():
    subprocess.run(["isort", "src"], check=True)
    subprocess.run(["black", "src"], check=True)
