from setuptools import setup, find_packages


setup(
    name='notes-server',
    description='Webplatform Notes Server',
    version=0.1,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

