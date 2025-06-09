import os
from setuptools import find_packages
from setuptools import setup

requirements = []

if os.path.isfile('requirements.txt'):
    with open('requirements.txt') as f:
        content = f.readlines()
    requirements.extend([x.strip() for x in content if 'git+' not in x])

if os.path.isfile('requirements_dev.txt'):
    with open('requirements_dev.txt') as f:
        content = f.readlines()
    requirements.extend([x.strip() for x in content if 'git+' not in x])


setup(name='legolas',
      version="0.0.1",
      description="LEGO: Locate And Sum (LEGOLAS)",
      license="MIT",
      # author="Le Wagon",
      # author_email="contact@lewagon.org",
      # url="https://github.com/coanda45/LegoLAS",
      install_requires=requirements,
      packages=find_packages(),
      test_suite="tests",
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      # scripts=['scripts/legolas-run'],
      zip_safe=False)
