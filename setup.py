from setuptools import setup

setup(name='relativeage',
      version='0.1',
      description='Relative age effect investigation.',
      url='https://github.com/NickAltmann/RelativeAgeEffect',
      author='Nick Altmann',
      author_email='nick@nickaltmann.net',
      license='MIT',
      packages=['relativeage'],
      install_requires=[
          'scipy', 'beautifulsoup4', 'pandas', 'requests', 'lxml', 'matplotlib', 'html5lib', 'pillow'
      ],
      zip_safe=True)
