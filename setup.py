from setuptools import setup

setup(name='gridrestore',
      version='0.1',
      description='Electric Grid Restoration Model',
      url='https://github.com/EnergyModels/blis',
      author='Jeff Bennett & Claire Trevisan',
      author_email='jab6ft@virginia.edu',
      license = 'MIT',
      packages=['gridrestore'],
      zip_safe=False,
      python_requires='~=2.7',
      install_requires=['pandas', 'numpy', 'matplotlib', 'seaborn'])