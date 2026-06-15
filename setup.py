from setuptools import setup, find_packages

setup(
    name="socialpilotbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiogram>=3.5.0",
        "aiohttp>=3.9.0",
    ],
    entry_points={
        "console_scripts": [
            "socialpilot=bot.main:main",
        ],
    },
)
