from setuptools import setup

setup(
    name='pydroneklv',
    version='0.1.0',
    description='Package to decode KLV packets from TS stream according to standard ST 0601.8',
    url='https://bitbucket.org/uavdevs/pydroneklv',
    author='Diogo Silva',
    author_email='dasilva@emfa.pt',
    license='',
    packages=['pydroneklv'],
    install_requires=['av'
                      ],

    classifiers=[
        'Development Status :: 1 - Early development',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
)