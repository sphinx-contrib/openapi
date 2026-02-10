OpenAPI Examples
================

A copy of the examples taken from `github.com/OAI/learn.openapis.org`__

This can be updated like so:

.. code-block:: bash

   # clone repo
   git clone --depth 1 https://github.com/OAI/learn.openapis.org.git /tmp/learn-openapis

   # copy updates
   rm -rf tests/examples
   cp -r /tmp/learn-openapis/examples tests/examples

   # store commit
   echo "https://github.com/OAI/learn.openapis.org/tree/$(git -C /tmp/learn-openapis rev-parse HEAD)/examples" > tests/examples/.source

   # restore README and remove unnecessary index file
   git checkout -f HEAD -- tests/examples/README.rst
   rm tests/examples/index.md

   # delete clone
   rm -rf /tmp/learn-openapis

.. __: https://github.com/OAI/learn.openapis.org.git
