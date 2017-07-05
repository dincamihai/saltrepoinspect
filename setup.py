from setuptools import setup

setup(name='saltrepoinspect',
      version='0.1',
      description='Tools to inspect a salt rpm repository',
      url='https://github.com/dincamihai/saltrepoinspect.git',
      author='Mihai Dincă',
      author_email='dincamihai@gmail.com',
      license='MIT',
      packages=['saltrepoinspect'],
      install_requires=[
          'requests',
          'beautifulsoup4'
      ],
      zip_safe=False)
