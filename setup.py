from setuptools import setup, find_packages

setup(
    name='scrapyautodb',
    version='0.0.1',
    keywords='scrapy peewee sqlite postgresql mysql',
    description='Export items to database using peewee',
    license='MIT License',
    url='https://github.com/Pandaaaa906/ScrapyAutoDb',
    author='Pandaaaa906',
    author_email='geekluca@qq.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=["peewee"],
)
