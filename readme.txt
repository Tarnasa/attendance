==================================================
|          ACM SIG-Sec Attendance Server         |
==================================================

To use, create a keys.json file with contents like the following:

['key1', 'key2']

Where key1 and key2 are keys that users must enter in order to sign-in.
When a user signs in, their info will be added to a key1.json file.

To run the server, just run

$ python server.py

