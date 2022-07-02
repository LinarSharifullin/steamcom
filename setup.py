from setuptools import setup


setup(
    name='steamcom',
    packages=['steamcom'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'rsa',
        'pycryptodomex'
    ]
)
