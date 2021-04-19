#!/usr/bin/env python
from setuptools import setup, find_namespace_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Stream Machine B.V.",
    author_email='apis@streammachine.io',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
    description=" Common Schema for Stream Machine driver",
    install_requires=[
        "streammachine-schemas-common==0.0.3",
        "requests>=2.24.0",
        "aiohttp>=3.6.2",
        "avro-python3>=1.10.0",
        "jsonschema>=3.2.0",
        "pytz>=2020.1",
        "pbr>=5.5.0",
        "six>=1.15.0",
        "responses>=0.10.15",
        "setuptools>=47.3.1",
        "pydantic>=1.5.1",
        "avro-json-serializer==1.0.3",
        "avro-python3>=1.10.0",
        "janus>=0.5.0"
    ],
    long_description=readme,
    include_package_data=True,
    keywords='streammachine api client driver',
    name='streammachine-driver',
    packages=find_namespace_packages(include=['streammachine.*']),
    namespace_packages=["streammachine"],
    setup_requires=[],
    version='0.0.10',
    zip_safe=False,
)
