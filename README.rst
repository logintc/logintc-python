Introduction
============

The LoginTC Python client is a complete LoginTC `REST API <https://www.logintc.com/docs/rest-api>`_ client to manage LoginTC organizations, users, domains, tokens and to create login sessions.

Installation
============

The libraries can be installed using the standard Python module installation method, `Distutils <http://docs.python.org/2/install/index.html>`_. Note that you will also need to have `setuptools <https://pypi.python.org/pypi/setuptools>`_ installed

::

    git clone https://github.com/logintc/logintc-python.git
    cd logintc-python
    python setup.py install

Alternatively, you should also be able to retrieve it from the Python Package Index via ``easy_install logintc`` or ``pip install logintc``

Example
=======

The following example will create an authentication session and wait 60 seconds for the user to approve or deny.

.. code:: python

    import logintc
    import datetime
    import time
    
    apiKey = 'LWbSCedV8sgFxdu0mPB42wuVWG7o3hf2AyaWKeHc0k6XgUHGZQj6K3yMOqPXY4Fq'
    domainId = '892e643b2da3547a705ba8f05316187976e11ec4'
    
    client = logintc.LoginTC(apiKey)
    session = client.create_session(domainId, username='john.doe')
    
    timeout = datetime.datetime.today() + datetime.timedelta(seconds=60)
    
    while datetime.datetime.today() < timeout:
        time.sleep(1)
        session = client.get_session(domainId, session['id'])
        if session['state'] == 'approved':
            print 'Approved!'
            break
        elif session['state'] == 'denied':
            print 'Denied!'
            break
        elif session['state'] == 'pending':
            print 'Waiting...'


Documentation
=============

See https://www.logintc.com/docs

If you have `Sphinx <http://sphinx-doc.org/>`_ installed, you can run ``make html`` from the root directory to generate the API documentation for the library locally.

Help
====

Email: support@cyphercor.com

https://www.logintc.com
