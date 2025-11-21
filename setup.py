from setuptools import setup, find_packages

setup(
    name="scrapgate_plugin",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "Flask_SQLAlchemy",
        "Flask-Limiter",
        "pyjwt",
    ],
    entry_points={
        "console_scripts": [
            "scrapgate=scrapgate.app:main",  # or your app run function
        ],
    },
)
