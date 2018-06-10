from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='veripress',
    version='1.0.7',
    packages=find_packages(),
    url='https://github.com/veripress/veripress',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
