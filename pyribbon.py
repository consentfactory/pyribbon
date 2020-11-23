import requests
import xmltodict

class pyribbon():
    
    def __init__(self,host,username,password,verify=False):

        self.host = host
        self.username = username
        self.password = password
        self.url = f"https://{host}/rest"
        self.session = requests.Session()
        self.verify = verify

    # Establish connection with SBC
    def open(self):
        
        auth = {"Username": self.username,"Password": self.password}
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8" }
        response = self.session.post(f"{self.url}/login", data=auth, headers=headers, verify=self.verify)
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            status = f"\nSuccessfully connected to {self.host}.\n"
            return status
        else:
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")

    # Closes connection with SBC
    def close(self):

        response = self.session.post(f"{self.url}/logout")
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            self.session.close()
            status = f"\nSuccessfully closed connection to {self.host}.\n"
            return status
        else:
            self.session.close()
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")

    # Queries (GET)
    def query(self,resource,details=False,filters=False):

        # Performs different GET requests depending on values sent
        if (details != False) and (filters != False):
            response = self.session.get(f"{self.url}/{resource}?details={details}&filter={filters}")
        elif (details != False):
            response = self.session.get(f"{self.url}/{resource}?details={details}")
        elif (filters != False):
            response = self.session.get(f"{self.url}/{resource}?filter={filters}")
        else:
            response = self.session.get(f"{self.url}/{resource}")
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            return response
        else:
            self.session.close()
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")

    # Creates (PUT)
    def create(self,resource,data):

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.put(f"{self.url}/{resource}",headers=headers,data=data)
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            return response
        else:
            self.session.close()
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
    
    # Updates (POST)
    def update(self,resource,data):

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.post(f"{self.url}/{resource}",headers=headers,data=data)
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            return response
        else:
            self.session.close()
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
    
    # Deletes (DELETE)
    def delete(self,resource):

        response = self.session.delete(f"{self.url}/{resource}")
        response.raise_for_status()
        self.status_code_check(response)
        if self.rest_status_code == "200":
            status = f"\nSuccess deleting:\n{self.url}/{resource}.\n"
            return status
        else:
            self.session.close()
            # If receiving non-200 code, raise exception and print status/error codes
            raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                f"Application Error Code: {self.app_error_code}\n"
                "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
    
    # Performs an action (POST)
    def action(self,resource,action,data=None,files=None):

        # Checking if there is a file uploaded
        # If there is a file, run the action with file upload and data provided
        if files is not None:
            filename = (files['Filename']).name
            response = self.session.post(f"{self.url}/{resource}?action={action}",data=data,files=files)
            response.raise_for_status()
            self.status_code_check(response)
            if self.rest_status_code == "200":
                status = f"\nSuccess uploading file {filename}.\nURL: {self.url}/{resource}?action={action}."
                return status
            else:
                self.session.close()
                # If receiving non-200 code, raise exception and print status/error codes
                raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                    f"Application Error Code: {self.app_error_code}\n"
                    "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
        
        # If no file, check for data and run the action with the data
        # If action is a backup but no data var sent, perform this to capture data
        # There could be other actions without data var, but not known currently
        elif (data is not None) or ((action == 'backup') and (data is None)):
            response = self.session.post(f"{self.url}/{resource}?action={action}",data=data)
            response.raise_for_status()
            # If data isn't sent, encoding will be UTF-8 with error information
            # Leaving '200' success in case some other behavior occurs
            if response.encoding != None:
                self.status_code_check(response)
                if self.rest_status_code == "200":
                    print(f"\nUnknown \'200\' status.\nURL: {self.url}/{resource}?action={action}.\n")
                    return response
                else:
                    self.session.close()
                    # If receiving non-200 code, raise exception and print status/error codes
                    raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                        f"Application Error Code: {self.app_error_code}\n"
                        "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
            else:
                print("\nSending data...\n")
                return response
        
        # If no data or file, run the action
        else:
            response = self.session.post(f"{self.url}/{resource}?action={action}")
            response.raise_for_status()
            self.status_code_check(response)
            if self.rest_status_code == "200":
                status = f"\nSuccess performing action: \"{action}\"\nURL: {self.url}/{resource}?action={action}.\n"
                return status
            else:
                self.session.close()
                # If receiving non-200 code, raise exception and print status/error codes
                raise ValueError(f"\n\nREST API error. Status code: {self.rest_status_code}\n"
                    f"Application Error Code: {self.app_error_code}\n"
                    "More info: https://support.sonus.net/display/UXAPIDOC/Application+Error+Codes\n")
    
    # Used for converting XML to dictionary
    def xml_to_dict(self,response):

        # Removing blank lines
        xml = response.content.strip()
        # Fixes 'ExpatError' from encoding issues in URL within XML
        xml = xml.replace(b'&',b'&amp;')
        dict_info = xmltodict.parse(xml, dict_constructor=dict)
        return dict_info
    
    # Parses response from SBC to look for status codes
    def status_code_check(self,response):
        
        status_code = self.xml_to_dict(response)
        try:
            # Looks dirty here, but got the job done.
            # Gets error code from SBC if there is an error
            self.app_error_code = status_code['root']['status'].get('app_status').get('app_status_entry').get('@code')
        except:
            pass
        self.rest_status_code = status_code = status_code['root']['status']['http_code']
