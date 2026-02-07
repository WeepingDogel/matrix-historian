from setuptools import setup, find_packages

setup(
    name="matrix-historian-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy==2.0.40",
        "pydantic==2.11.4",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.1.0",
    ],
)
