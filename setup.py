from setuptools import setup

setup(
    name='veripress',
    version='1.0.1',
    packages=['veripress', 'veripress.api', 'veripress.model', 'veripress.view', 'veripress_cli'],
    url='https://github.com/veripress/veripress',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    install_requires=[
        'Flask', 'Flask-Caching', 'PyYAML', 'mistune', 'Pygments', 'feedgen'
    ],
    include_package_data=True,
    platforms='any',
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    )
)
