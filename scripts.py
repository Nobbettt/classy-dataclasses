# scripts.py
import subprocess


def lint():
    subprocess.run(["black", "classy_dataclasses"])


def test():
    subprocess.run(["poetry", "run", "pytest"])
    subprocess.run(["tox"])
