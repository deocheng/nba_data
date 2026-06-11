from setuptools import setup, find_packages

setup(
    name='nba_data_importer',
    version='1.0.0',
    description='通用NBA数据导入应用',
    author='NBA Data Team',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl',
        'psycopg2-binary',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'data_importer=data_importer.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
