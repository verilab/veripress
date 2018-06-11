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
        'Flask', 'Flask-Caching', 'PyYAML', 'markdown',
        'Pygments', 'pytz'
    ],
    python_requires='>=3.4',
    include_package_data=True,
    platforms='any',
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    )
)
