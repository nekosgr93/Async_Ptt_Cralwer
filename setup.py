from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    description = f.read()

setup(
    name="Async_Ptt_Crawler",
    version="1.3",
    author="nekosgr93",
    description='Ptt Crawler base on asyncio and use async/await syntax',
    long_description=description,
    packages=['Ptt_Crawlers'],
    install_requires=['beautifulsoup4', 'aiohttp', 'lxml'],
    python_requires='>=3.5',
    url="https://github.com/nekosgr93/Async_Ptt_Cralwer"
)
