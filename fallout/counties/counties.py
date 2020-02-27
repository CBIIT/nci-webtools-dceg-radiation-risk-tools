import os
import sys
import pyodbc
import us

# First, add the base directory to the python path, so it finds the fallout module.
base_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
trio_dir = os.path.join(base_dir, 'fallout')
sys.path.insert(0, base_dir)
sys.path.insert(0, trio_dir)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fallout.settings")
django.setup()

if __name__ == "__main__":
    from fallout.calculator.models import State, County
    
    conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s' % (sys.argv[1],))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM counties;') # id, state abbreviation, county name
    for row in cursor.fetchall():
        try:
            state = State.objects.get(abbreviation=row[1])
            County.objects.get_or_create(state=state, name=row[2])
        except State.DoesNotExist:
            us_state = us.states.lookup(row[1])
            if not us_state:
                print('unable to find state for %s' % row[1])
            else:
                state = State.objects.create(abbreviation=row[1], name=us_state.name)
                County.objects.get_or_create(state=state, name=row[2])

    State.objects.get_or_create(abbreviation='OU', name='Outside Study Area')