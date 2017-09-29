from setuptools import setup

setup(
    name='Udacity Catalog',
    version='0.7',
    packages=['Catalog'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    'Flask>=0.2',
    'SQLAlchemy>=0.6',
    'Passlib',
    'ItsDangerous',
    'Redis',
    'Flask_HTTPAuth'
    ]
)
