from setuptools import setup, find_packages

with open("README.md") as readme_file:
    README = readme_file.read()

with open("history.md") as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name="pymcws",
    version="0.2.0",
    description="Python API for the MCWS interface of JRiver Media Center",
    long_description_content_type="text/markdown",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    packages=find_packages(),
    author="Keno März",
    author_email="keno.maerz@gmail.com",
    keywords=["JRiver", "MCWS"],
    url="https://github.com/kenomaerz/pymcws",
    download_url="https://pypi.org/project/pymcws/",
)

install_requires = ["requests", "pillow"]

if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)
