from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='veripress',
    version='1.0.11',
    packages=find_packages(),
    url='https://github.com/veripress/veripress',
    license='MIT License',
    author='Richard Chien',
    author_email='richardchienthebest@gmail.com',
    description='A blog engine for hackers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'Flask>=1.1,<1.2', 'Werkzeug>=0.16,<1.0', 'Flask-Caching>=1.4,<2.0',
        'PyYAML>=5.3,<6.0', 'Markdown>=3.2,<4.0', 'Pygments>=2.5,<2.6',
        'pytz>=2019.3,<2020.0', 'click>=7.0,<8.0'
    ],
    python_requires='>=3.4',
    include_package_data=True,
    platforms='any',
    entry_points=dict(
        console_scripts=['veripress=veripress_cli:main']
    ),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    )
)
