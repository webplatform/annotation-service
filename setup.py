from setuptools import setup, find_packages


setup(
    name='notes-server',
    description='Webplatform Notes Server',
    version=0.1,
    packages=find_packages(),

    install_requires=[
        'requests_oauthlib>=0.4.0',
    ],

    include_package_data=True,
    zip_safe=False,
)

