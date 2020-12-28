from setuptools import setup, find_packages

py_modules=(
    'child_stats',\
    'data_dict',\
    'data_fetcher',\
    'entry_validator',\
    'gender_dict',\
    'gui_content',\
    'gui_tools',\
    'match_names',\
    'name_lists',\
    'read_stats',\
    'setup',\
    'stat_table',\
    'table_operations',\
    )

setup(
    name='aenir2',\
    description='A Fire Emblem average stats calculator',\
    url='https://github.com/gchang12/aenir2',\
    author='gchang12',\
    packages=find_packages(include=('dracogate','quintessence')),\
    py_modules=py_modules,\
    install_requires=('numpy','pandas','requests','bs4','tkinter'),\
    include_package_data=True
    )


if __name__ == '__main__':
    x=4
