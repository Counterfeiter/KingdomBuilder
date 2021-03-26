from distutils.core import setup

setup(
    name='KingdomBuilder',
    version='0.0.1',
    description='Kingdom Builder Board Game - rules and cli playable',
    url='https://github.com/counterfeiter/kingdombuilder',
    author='Sebastian Förster',
    packages=['kingdombuilder',],
    license='MIT',
    long_description=open('README.md').read(),
)