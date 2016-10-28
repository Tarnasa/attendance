"""
This class handles requests for the /signin/ page.

The signin page allows users to input their:
    Name
    Email
    Major
Along with the option to "add me to the sig-sec mailing list"
And requires the users to provide a "secret key" which will be available only
to people actually at the event (via writing it on the whiteboard or something)

In order to successfully sign-in the user's "secret key" is compared against
a list of secret keys which are listed in the file "keys.json" which is a file
of the following json format:

["key1", "key2"]

If the user submits this information, it is stored in a json file under the
name "{secret}.json" in the following json format:

{
    "attendees": [
    {
        "ip": "127.0.0.1", 
        "major": "CS", 
        "name": "Dave", 
        "add_to_sig_sec": true, 
        "secret": "H4CK1T", 
        "time": "2016-10-07 01:04:09", 
        "email": "dave@mst.edu"
    }
    ]
}
"""
import string
from datetime import datetime, timedelta
import json
import os

key_filename = 'keys.json'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Handler:
    def __init__(self):
        self.html = open('signin.html', 'rb').read()
        #self.html = open('index.html', 'rb').read()
        class CustomTemplate(string.Template):
            delimiter = '$$'
        self.template = CustomTemplate(self.html)
        self.keys = self.read_keys()
        self.custom_headers = False
        self.required_fields = ['secret', 'major', 'name', 'email']
    
    def read_keys(self):
        with open(key_filename, 'r') as f:
            data = json.loads(f.read())
        return data

    def update_attendance(self, key, new_record):
        filename = "{}.json".format(key)
        if not os.path.exists(filename):
            data = {'attendees': []}
        else:
            with open(filename, 'r') as f:
                data = json.loads(f.read())
        data['attendees'].append(new_record)
        with open("{}.json".format(key), 'w') as f:
            f.write(json.dumps(data, indent=4))

    def generate_html(self, **d):
        """ Fill in input fields with data in d """
        # Default values
        params = {
                'response': '',
                'secret': '',
                'major': '',
                'name': '',
                'email': '',
                'add_to_ccdc': 'False',
                'add_to_cdt': 'False',
                'add_to_sig_sec': 'False'}
        d['ccdc_checked'] = 'checked' if 'add_to_ccdc' in d else ''
        d['cdt_checked'] = 'checked' if 'add_to_cdt' in d else ''
        d['sec_checked'] = 'checked' if 'add_to_sig_sec' in d else ''
        params.update(d)
        # Escape quotes for inserting into html
        for field in self.required_fields:
            params[field] = params[field].replace('"', '&quot;')
        return self.template.substitute(**params)

    def handle(self, handler, get_vars, post_vars):
        if handler.command == 'GET':
            handler.wfile.write(self.generate_html())
            return
        if handler.command == 'POST':
            # Simplify post_vars
            post_vars = {k: v[0] for k, v in post_vars.items()}
            print(post_vars)
            # Check for required fields
            for field in self.required_fields:
                if field not in post_vars or post_vars[field].strip() == '':
                    handler.wfile.write(self.generate_html(
                        response='{} is required'.format(field),
                        **post_vars))
                    return
            # Check secret key
            self.keys = self.read_keys()
            if post_vars['secret'] not in self.keys:
                handler.wfile.write(self.generate_html(
                    response='The secret was not recognized',
                    **post_vars))
                return
            # Save new data
            data = {
                    'secret': post_vars['secret'],
                    'major': post_vars['major'],
                    'name': post_vars['name'],
                    'email': post_vars['email'],
                    'add_to_ccdc': 'add_to_ccdc' in post_vars,
                    'add_to_cdt': 'add_to_cdt' in post_vars,
                    'add_to_sig_sec': 'add_to_sig_sec' in post_vars,
                    'time': datetime.now().strftime(DATE_FORMAT),
                    'ip': handler.client_address[0],
                    }
            self.update_attendance(post_vars['secret'], data)
            # Show success message
            handler.wfile.write(self.generate_html(response='Successfully signed in!')) 
            return
