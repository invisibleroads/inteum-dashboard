'Command-line script to upload data'
import simplejson
from urllib2 import urlopen
from urllib import urlencode
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
    post('upload', dict(token=token, payload=simplejson.dumps(payload)))
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
    class Company(Base):
        __table__ = tables['COMPANY']
    class Contact(Base):
        __table__ = tables['CONTACTS']
    class Country(Base):
        __table__ = tables['COUNTRY']
    class Phone(Base):
        __table__ = tables['PHONES']
    class Technology(Base):
        __table__ = tables['TECHNOLOGY']
    class Patent(Base):
        __table__ = tables['PATENTS']
    class PatentInventor(Base):
        __table__ = tables['PATINV']
    class PatentType(Base):
        __table__ = tables['PAPPTYPE']
    class PatentStatus(Base):
        __table__ = tables['PATSTAT']
    DBSession = sessionmaker(engine)
    db = DBSession()
    # Load companies
    companies = []
    for company in db.query(Company):
        companies.append((
            company.PRIMARYKEY,
            company.NAME))
    # Load contacts
    contacts = []
    for contact in db.query(Contact):
        contacts.append((
            int(contact.PRIMARYKEY),
            contact.FIRSTNAME.strip(),
            contact.MIDDLEINI.strip(),
            contact.LASTNAME.strip(),
            contact.EMAIL.strip()))
    # Load countries
    countries = []
    for country in db.query(Country):
        countries.append((
            int(country.PRIMARYKEY),
            country.NAME.strip()))
    # Load patents
    patents = []
    for patent in db.query(Patent):
        patents.append((
            int(patent.PRIMARYKEY),
            int(patent.TECHNOLFK),
            patent.NAME.strip(),
            int(patent.LAWFIRMFK),
            patent.LEGALREFNO.strip(),
            patent.FILEDATE.strftime('%Y%m%d'),
            int(patent.PATSTATFK),
            int(patent.PAPPTYPEFK)
            int(patent.COUNTRYFK)))
    # Load patentInventors
    patentInventors = []
    for patentInventor in db.query(PatentInventor):
        patentInventors.append((
            int(patentInventor.PATENTSFK),
            int(patentInventor.CONTACTSFK),
            int(patentInventor.PI_ORDER)))
    # Load patentStatuses
    patentStatuses = []
    for patentStatus in db.query(PatentStatus):
        patentStatuses.append((
            int(patentStatus.PRIMARYKEY),
            patentStatus.NAME.strip()))
    # Load patentTypes
    patentTypes = []
    for patentType in db.query(PatentType):
        patentTypes.append((
            int(patentType.PRIMARYKEY),
            patentType.NAME.strip()))
    # Load phones
    phones = []
    for phone in db.query(Phone):
        phones.append((
            int(phone.PRIMARYKEY),
            int(phone.CONTACTSFK),
            phone.PHONENUM.strip(),
            phone.PHONETYPE.strip()))
    # Load technologies
    technologies = []
    for technology in db.query(Technology):
        technologies.append((
            int(technology.PRIMARYKEY),
            technology.TECHID.strip(),
            technology.NAME.strip()))
    # Return
    payload = {
        'companies': companies,
        'contacts': contacts,
        'countries': countries,
        'patents': patents,
        'patentInventors': patentInventors,
        'patentStatuses': patentStatuses,
        'patentTypes': patentTypes,
        'phones': phones,
        'technologies': technologies,
    }
    countByKey = {
        'companies': len(companies),
        'contacts': len(contacts),
        'countries': len(countries),
        'patents': len(patents),
        'patentInventors': len(patentInventors),
        'patentStatuses': len(patentStatuses),
        'patentTypes': len(patentTypes),
        'phones': len(phones),
        'technologies': len(technologies),
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
