from setuptools import setup

setup(name='relative_age',
      version='0.1',
      description='Relative age effect investigation.',
      url='https://github.com/NickAltmann/RelativeAgeEffect',
      author='Nick Altmann',
      author_email='nick@nickaltmann.net',
      license='MIT',
      packages=['relative_age'],
      install_requires=[
          'scipy', 'beautifulsoup4', 'pandas', 'requests', 'lxml'
      ],
      zip_safe=False)