pyribbon: Python Module for Sonus/Ribbon SBC REST API
=

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Methods](#methods)
  * [Open](#open)
  * [Close](#close)
  * [Query](#query)
  * [Create](#create)
  * [Update](#update)
  * [Delete](#delete)
  * [Action](#action)
- [Error Handling](#error-handling)
- [Links](#links)
- [Potential Issues](#potential-issues)
- [Disclaimer](#disclaimer)


# Overview

`pyribbon` is a Python module that interacts with Sonus/Ribbon SBC REST API to query for data, create/update resources, and even perform reboots, configuration backups and restores within a Python framework.

# Prerequisites

* Python Requirements
  * Python 3.6.9+ (Tested on 3.6.9)
  * Python Modules
    * requests
    * xmltodict
* Knowledge of Sonus/Ribbon API and SBC
* Sonus/Ribbon
  * SBC/UX 1000/2000/SWe Lite running 5.0.1 or newer
    * Tested and known to work on SBC 2000s running 7.x and 8.x.
    * [Ribbon SBC 1K/2K/SWe Lite Requirements](https://support.sonus.net/display/UXDOC90/REST+API+-+Requirements)
      * Enable user with REST access level. Can be local user or LDAP/AD user.
      * HTTPS - Module uses HTTPS for all http requests.
  * NOT TESTED on SBC 5000/7000/SWe, but from my look at the API docs it should work
    * [Ribbon SBC 5k/7k/SWe Requirements](https://support.sonus.net/display/SBXAPIDOC/REST+API+Requirements)
* Not required, by I highly recommend you use [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/) for this.


# Methods

Here's a quick overview of the methods:

* **open**: Establishes a session with the SBC.
* **close**: Closes and disconnects the session with the SBC.
* **query**: Queries/looks up resources.
* **create**: Creates resources or adds entries to resources.
* **update**: Updates/modifies resources.
* **delete**: Deletes resources.
* **action**: Performs an action on a resource.

> Note: the documentation below is written using SBC 2000 and from Linux workstation. Adapt to your environment accordingly.

## Open

Establishes a session with the SBC.

```python
  pyribbon.open(host,username,password,verification)
```

Example:

```python
def session_creator():
    
    # Hostname or IP Address
    host = "sbc.consentfactory.com"
    # Must be user account with REST access level. Administrator accounts will not work. 
    username = "jimmy"
    # Plain-text password or getpass() for password.
    from getpass import getpass()
    password = getpass()
    #password = "superstrongpassword12345"
    # Optional setting here. If using internal PKI, point to root CA certificate, otherwise omit. See note below.
    verification = "/home/jimmy/rootCA.pem"
    
    # If omitting 'verification', remove verification variable below
    session = pyribbon(host,username,password,verification)

    # Open Session
    open_response = session.open()
    print(open_response)

    return(session)

```
### Verification

`pyribbon` uses the `requests` module to establish a HTTPS connection with the SBC and will thus attempt to verify certificates. If you omit `verification`, the default value will be 'False' and you will receive an error similar to this:

```
/home/jimmy/.env/pyribbon/lib/python3.6/site-packages/urllib3/connectionpool.py:988: InsecureRequestWarning: Unverified HTTPS request is being made to host 'sbc.consentfactory.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning,
```
To avoid this error, provide a path to the certificate for the root/issuing certificate authority like in the example above.

## Close

Closes and disconnects the session with the SBC.

```
  pyribbon.close()
```

Example:

```python
def main():
  
  #
  # Bunch of code...
  #

  close_response = session.close()
  print(close_response)
```

## Query

Queries/looks up resources.

```
  pyribbon.query(resource,details,filter)
```
The parameter `resource` is the API resource path to lookup.

The `pyribbon.query()` method obtains data from the SBC and returns the data in XML format. In the Ribbon API documentation, all queries will be listed as 'GET' requests in the resource documentation.

Example:

```python
def main():

    # Looking up a routing entry in a routing table
    # Documentation: https://support.sonus.net/display/UXAPIDOC/Resource+-+routingentry
    q_resource = "routingtable/1/routingentry/1"
    get_response = session.query(q_resource)
    print(get_response.text.strip())

```

### Details and Filters
Some queries/GET requests have additional parameters to be added to a query. In particular for queries/GET requests there are two additional optional parameters in the `pyribbon.query()` method: `details` and `filters` (Python has a `filter()` function, so `filters` is used instead). These parameters are not available to all queries, so you'll need to look through the API documentation to find them. 

The parameter `details` will print off all detailed information for each entry in a parent resource list as part of a bulk request. To use `details` for a whole list of resources, set the details parameter to `true`.

> Note: the REST API is case-sensitive. If you send 'True', the SBC API will fail with a 400 status code, 20035 application error code. `details` has to be set to '**true**'.

`details` example:

```python
def main():

    # Looking up a routing entry in a routing table
    # Documentation: https://support.sonus.net/display/UXAPIDOC/Resource+-+routingentry
    q_resource = "routingtable"
    get_response = session.query(q_resource,details="true")
    print(get_response.text.strip())

```

The parameter `filters` (or `filter` in REST API call, as noted int the [Ribbon documentation](https://support.sonus.net/display/UXDOC61/Sonus+SBC+Edge+API+-+Resource+Design#SonusSBCEdgeAPI-ResourceDesign-3.1.4CategoriesofResourceAttributes)) is used for either bulk requests (`details`) or with single resources. You can only ever provide one of the following in the `filter` parameter: `configuration`, `runtime`, `statistics` or `inventory`. Like `details` above, there are certain resources that use `filters` that you will need to lookup.

`filters` example:

```python
def main():

    # Looking up the SIP signal group table and getting statistics
    # Documentation: https://support.sonus.net/display/UXAPIDOC/GET+sipsg
    q_resource = "sipsg/1"
    get_response = session.query(q_resource,filters="statistics")
    print(get_response.text.strip())

```

`details` and `filters\filter` example:

```python
def main():

    # Looking up the ISDN signal group table and getting statistics
    # Documentation: https://support.sonus.net/display/UXAPIDOC/Resource+-+isdnsg
    q_resource = "isdnsg"
    get_response = session.query(q_resource,details='true',filters="statistics")
    print(get_response.text.strip())

```

## Create

Creates resources or adds entries to resources.

```
  pyribbon.create(resource,data)
```

The parameter `resource` is the API resource to create, and `data` is a dictionary of key-values related to the API resource/resource entry. It is recommended that you use [r strings (raw strings)](https://www.askpython.com/python/string/python-raw-strings) for your resource paths, otherwise you'll encounter URL encoding errors. 

In the Ribbon API documentation, all resource creation will be listed as 'PUT' requests in the resource documentation.

In the example below, we're adding a transformation table entry within a transformation table resource. 

Example:

```python
def main():

    # Creates a transformation table entry in a transformation table, but leaves it disabled
    # Documentation: https://support.sonus.net/display/UXAPIDOC/Resource+-+transformationentry
    c_resource = r"transformationtable/8"
    c_resource_entry =  r"transformationentry/2"
    c_resource_entry_data = {
        'Description': r'TEST123 ENTRY DESCRIPTION',
        'InputFieldValue': '0',
        'InputFieldValue': r'^(18001234567)',
        'OutputFieldValue': r'\1',
        'ConfigIEState': '0'
    }

    output = session.create(f"{c_resource}/{c_resource_entry}",c_resource_entry_data)
    # The XML returned has a lot leading and ending blank space. Using .text.strip() to remove that.
    print(output.text.strip())
```

## Update

Updates/modifies resources. 

```
  pyribbon.update(resource,data)
```

The parameter `resource` is the API resource to create, and `data` is a dictionary of key-values related to the API resource/resource entry. It is recommended that you use [r strings (raw strings)](https://www.askpython.com/python/string/python-raw-strings) for your resource paths, otherwise you'll encounter URL encoding errors.

In the Ribbon API documentation, all updates will be listed as 'POST' requests in the resource documentation.

In example below, we're updating the description for the transformation table entry. 

Example:

```python
def main():

  # Updates the description for a transformation entry in a transformation table resource
  # Documentation: https://support.sonus.net/display/UXAPIDOC/Resource+-+transformationentry
  u_resource = r"transformationtable/7/transformationentry/1"
  u_resource_data = {'Description:'UPDATE TEST Entry DESCRIPTION 7'}
  print(u_resource_data)
  output = session.update(u_resource,u_resource_data)
  print(output.text.strip())
```

## Delete

Deletes resources.

```
  pyribbon.delete(resource)
```

The parameter `resource` is the API resource to delete. 

Example:

```python
def main():

  d_resource = r"transformationtable/8"
  d_resource_entry =  r"transformationentry/2"
  output = session.delete(f"{p_resource}/{p_resource_entry}")
  print(output.text.strip())
```

## Action

Performs an action on a resource.

```
  pyribbon.action(resource,action,data,files)
```

Action parameters:

  * `resource`: API resource to perform action on
  * `data`: Dictionary of key-values sent
  * `files`: Dictionary of key-values, with values being file data

The `pyribbon.action()` method has basically three categories of actions:

  * Simple action (e.g., reboot)
  * Action with parameters sent (data) that returns files (e.g., backup)
  * Action with parameters and files sent to device (e.g., restore)

Most actions are going to involve the [system resource](https://support.sonus.net/display/UXAPIDOC/Resource+-+system), but some resources will have actions (e.g., [isdnsg](https://support.sonus.net/display/UXAPIDOC/POST+isdnsg+-+action+resetcounters) to reset counters).

Simple action example:

```python
def main():

  # Reboots the SBC
  # Documentation: https://support.sonus.net/display/UXAPIDOC/POST+system+-+action+reboot
  a_resource = "system"
  a_action = "reboot"
  output = session.action(resource=a_resource,action=a_action)
  print(output)
```

Example action for getting data returned:

```python
def main():

  # Creates a backup of the SBC configuration
  # Documentation: https://support.sonus.net/display/UXAPIDOC/POST+system+-+action+backup
  a_resource = "system"
  a_action = "backup"
  a_data = {"Passphrase":'superSecretAndSecurePassword123'}
  output = session.action(resource=a_resource,action=a_action,data=a_data)
  data_headers = output.headers['content-disposition']
  filename = (re.findall("filename=(.+)", data_headers)[0]).replace(";","")
  data = output.content
  with open(filename,'wb') as f:
      f.write(data)
  print("Backup saved.\n")
```

Example action sending file:

```python
def main():

  # Uploads a configuration backup that was downloaded with a password
  # Documentation: https://support.sonus.net/display/UXAPIDOC/POST+system+-+action+restore
  filename = "SBC_Config_sbc_8.1.5_b538_2020_11_17.tar"
  print(f"Uploading {filename}...")
  a_upload_resource = "system"
  a_upload_action = "restore"
  a_upload_data = {"Passphrase":'superSecretAndSecurePassword123'}
  a_upload_file = {'Filename': open(filename, 'rb')}
  output = session.action(
      resource=a_upload_resource,
      action=a_upload_action,
      data=a_upload_data,
      files=a_upload_file
  )
  print(output)
```

# Error Handling

The `pyribbon` module captures errors reported from the REST API by converting the XML to a dictionary, then parses the dictionary for the http status code. Anything reported by the REST API that is not a 200 code will cause the module to raise a Python exception and print the status code along with the [Ribbon application error code](https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes).

For example, let's make a query lookup from a resource on the SBC that does not have 'inventory' as a filter object:

```python
def main():

  q_resource = "sipsg"
  output = pyribbon.query(session,q_resource,details="true",filters="inventory")
  print(output.text.strip())
```

The module will return something like the following:

```
Traceback (most recent call last):
  File "/home/jimmy/dev/ribbon/sbc_config.py", line 214, in <module>
    main()
  File "/home/jimmy/pyribbon/sbc_config.py", line 46, in main
    get_response = session_query(session,q_resource,details="true",filters="inventory")
  File "/home/jimmy/pyribbon/sbc_config.py", line 31, in session_query
    get_response = session.query(q_resource,details,filters)
  File "/home/jimmy/pyribbon/pyribbon.py", line 65, in query
    raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
ValueError: 

REST API error. Status code: 400
Application Error Code: 20035
More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes
```

# Links

The methods are peppered with links to Ribbon resources regarding the REST API, but here are a few consolidated into one location. 

> **Note**: *the Ribbon API documentation is a little bit of a hot mess*.  
All the API documentation isn't consolidated into one location or into one tree structure. There are API documents related to the release versions, then there are guides within some versions, examples in one place, and then there's an overall API resource document -- it's just all confusing and needs a redesign. If you click on the page tree to the left, you'll get taken to different page structures and its easy to get lost. Below I'll try to give some structure it all.

### Ribbon API Overview

* Start here (for some reasons these documents are buried in 6.1.0 but you can't find them in 7.0-9.0):
  * API requirements for SBC 1K/2K  
  https://support.sonus.net/display/UXDOC61/Sonus+SBC+Edge+API+-+Requirements
  * API Design (required reading. Explains a lot of the API)  
  https://support.sonus.net/display/UXDOC61/Sonus+SBC+Edge+API+-+Resource+Design  
  * REST API Samples (these are `curl` examples, but useful for understanding the calls)  
  https://support.sonus.net/display/UXDOC61/Sonus+SBC+Edge+API+-+REST+Samples
* Reference Documentation
  * SBC 1000/2000 API Home (use this to get the details on creating your resource items)  
  https://support.sonus.net/pages/viewpage.action?pageId=17400591
  * Application Error Codes (if there's an issue with your API call, you'll get a code that you can lookup here)  
  https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes

# Potential Issues

* Code optimization: I'm sure there's stuff that could be better done. I welcome pull requests.
* Action method: have I captured all corner cases? Are there actions other actions besides backup that will return data without data being sent? I haven't tested every action, and the `action` method will throw an exception for actions that are sent using the 'simple' method (no `data` or `files`), but its returning a file for download.
* Non-error, non-200 status codes might need further work. I'm just treating the REST API statuses with a binary response: 200 or not. If it didn't work, error out. I don't think I'm wrong here, but I could be.

# Disclaimer

Use at your risk. You assume responsibility by using this. Blah blah blah disclaimer stuff. 