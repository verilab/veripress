from distutils.core import setup

setup(
    name='veripress',
    version='1.0.0',
    packages=['veripress', 'veripress_cli'],
    url='',
    license='The MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    install_requires=[
        'flask', 'flask-caching', 'pyyaml', 'mistune', 'pygments', 'feedgen'
    ],
    tests_require=[
        'pytest'
    ],
    include_package_data=True,
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    )
)
