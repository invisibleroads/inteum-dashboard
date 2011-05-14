'Command-line script to upload data'
import simplejson
from urllib2 import urlopen
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pyramid.url import route_url
from pyramid.testing import DummyRequest

import script_process
from tcd.libraries.tools import get_token


def run(settings):
    'Upload data to dashboard'
    countByKey = {}
    sqlalchemyURL = settings['tc.sqlalchemy.url']
    appURL = settings['tc.url']
    appUsername = settings['tc.username']
    appPassword = settings['tc.password']
    def post(name, valueByKey=None, expectJSON=True):
        url = route_url(name, DummyRequest(), _app_url=appURL)
        data = urlopen(url, valueByKey).read()
        if expectJSON:
            data = simplejson.loads(data)
            if options.verbose and not data.get('isOk'):
                return data.get('message')
        return data
    # Login
    post('user_login', dict(username=appUsername, password=appPassword))
    # Get token
    data = post('user_index', expectJSON=False)
    token = get_token(data)
    # Assemble
    payload, countByKey = assemble(sqlalchemyURL)
    # Upload
    post('upload', dict(token=token, payload=payload))
    # Logout
    post('user_logout')
    # Return
    return '\n'.join('%s: %s' % (key.capitalize(), count) for key, count in countByKey.iteritems())


def assemble(sqlalchemyURL):
    'Assemble payload'
    # Load tables
    Base = declarative_base()
    engine = create_engine(sqlalchemyURL)
    Base.metadata.reflect(engine)
    tables = Base.metadata.tables
    class Patent(Base):
        __table__ = tables['PATENTS']
    class PatentType(Base):
        __table__ = tables['PAPPTYPE']
    class PatentStatus(Base):
        __table__ = tables['PATSTAT']
    DBSession = sessionmaker(engine)
    db = DBSession()
    # Load patents
    patents = []
    for patent in db.query(Patent):
        patents.append((
            patent.PRIMARYKEY,
            patent.FILEDATE.strftime('%Y%m%d'),
            patent.PAPPTYPEFK,
            patent.PATSTATFK))
    # Load patentTypes
    patentTypes = []
    for patentType in db.query(PatentType):
        patentTypes.append((
            patentType.PRIMARYKEY, 
            patentType.NAME.encode('utf-8'))
    # Load patentStatuses
    patentStatuses = []
    for patentStatus in db.query(PatentStatus):
        patentStatuses.append((
            patentStatus.PRIMARYKEY, 
            patentStatus.NAME.encode('utf-8')))
    # Return
    payload = {
        'patents': patents,
        'patentTypes': patentTypes,
        'patentStatuses': patentStatuses,
    }
    countByKey = {
        'patents': len(patents),
        'patentTypes': len(patentTypes),
        'patentStatuses': len(patentStatuses),
    }
    return payload, countByKey


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.OptionParser()
    options = optionParser.parse_args()[0]
    # Run
    message = run(script_process.initialize(options))
    # Say
    if options.verbose:
        print message
