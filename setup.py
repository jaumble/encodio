from setuptools import setup

setup(
   name='textaudiotext',
   version='1.0',
   description='A shitty encoder',
   author='jumble',
   author_email='jumblesmail@gmail.com',
   packages=['textaudiotext'],  #same as name
   install_requires=['numpy', 'pyaudio'], #external packages as dependencies
)