from distutils.core import setup

setup(
    name='crypto_masher',
    version='0.1',
    packages=['crypto_masher'],
    url='https://github.com/vulogov/crypto_masher',
    license='GPL-3.0',
    author='Vladimir Ulogov',
    author_email='vladimir.ulogov@me.com',
    description='Slightly naive variable size block cipher',
    requires=[
        "quantumrandom",
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
        'Topic :: Security :: Cryptography',
    ]
)
