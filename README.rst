==============
orb-api-python
==============


see: http://mpowering.readthedocs.org/en/latest/restapi.html for more information

Installing
==========

For general purpose use and *development* just use in a virtual environment:

    make install

This will install the package for development as well as all testing requirements.

Otherwise run a full install:

    python setup.py install

Running the tests
=================

Recommended to install `tox <https://tox.readthedocs.io/en/latest/>`_, and tests can be run
using only the `tox` command.

The commands `pytest` or `make test` can be used to run the tests. The `make test` command
will also use coverage.

Using the CLI script
====================

Setup will install a command line script named `orb_cli` which allows rudimentary interaction
with an ORB API from the command line.

    orb_cli list --username=somebody --key=kjasdksjf

Run `orb_cli --help` for argument specifications.
