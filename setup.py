from setuptools import setup, find_packages
setup(
    name='goc',
    version='1.0',
    description='Game Of Code',
    author='Heera Jaiswal',
    include_package_data = True,
#    package_data={"": ["*.ini"]},
    install_requires=[                    
    			],
    #setup_requires=["virtualenv"],
    packages = find_packages()
    )