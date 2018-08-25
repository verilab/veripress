from setuptools import setup, find_packages

setup(
    name='veripress',
    version='1.0.8',
    packages=find_packages(),
    url='https://github.com/veripress/veripress',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    install_requires=[
        'Flask>=1.0.2', 'Werkzeug>=0.14.1', 'Flask-Caching>=1.4.0',
        'PyYAML>=3.13', 'markdown>=2.6.11', 'Pygments>=2.2.0',
        'pytz>=2018.5', 'click>=6.7'
    ],
    python_requires='>=3.4',
    include_package_data=True,
    platforms='any',
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    )
)
