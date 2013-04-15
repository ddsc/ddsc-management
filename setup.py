from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'ddsc-core',
    'django-celery',
    'django-extensions',
    'django-floppyforms == 1.0',
    'django-nose',
    'django-tables2',
    'django-treebeard',
    'gunicorn',
    'lizard-auth-client',
    'lizard-map',
    'lizard-ui',
    'python-memcached',
    'raven',
    'six',  # floppyforms secretly depends on this
    'werkzeug',
    ],

setup(name='ddsc-management',
      version=version,
      description="Management site for DDSC's backend data",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout.vanrees@nelen-schuurmans.nl',
      url='https://github.com/ddsc/ddsc-management',
      license='GPL',
      packages=['ddsc_management'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
          ]},
      )
