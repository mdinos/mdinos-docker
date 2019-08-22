from dateutil import parser
from datetime import datetime

def sanitise_user_input(**kwargs):
    if 'username' in kwargs:
        full_length = len(kwargs['username'])
        username = ''.join(char for char in kwargs['username'] if char not in [' ', '-', '_'])
        reduced_length = len(username)

        if not username.isalnum() or not 1 <= reduced_length <= 12 - (full_length - reduced_length) or not 1 <= len(kwargs['username']) <= 12:
            return (False, 'Bad input: Invalid username')

    if 'date_string' in kwargs:
        # Test if valid YYYY-MM-DD format
        try:
            date = parser.parse(kwargs['date_string'], dayfirst=False)
        except ValueError:
            return (False, 'Invalid date format; YYYY-MM-DD.')

        if len(kwargs['date_string']) != 10:
            return (False, 'Invalid date format; YYYY-MM-DD.')

        # Test if date is in the future
        today = datetime.now()
        if today < date:
            return (False, 'Date is in the future.')
    
    return True, 'Good input'

        
        
