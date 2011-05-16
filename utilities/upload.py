'Command-line script to upload data'
import simplejson
from urllib2 import urlopen
from urllib import urlencode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import script_process
from tcd import main
from tcd.libraries.tools import get_token


def run(settings):
    'Upload data to dashboard'
    countByKey = {}
    sqlalchemyURL = settings['tc.sqlalchemy.url']
    appURL = settings['tc.url']
    appUsername = settings['tc.username']
    appPassword = settings['tc.password']
    def post(relativeURL, valueByKey=None, expectJSON=True):
        url = appURL + '/' + relativeURL
        data = urlopen(url, urlencode(valueByKey or {})).read()
        if expectJSON:
            data = simplejson.loads(data)
            if options.verbose and not data.get('isOk'):
                return data.get('message')
        return data
    # Login
    post('users/login', dict(username=appUsername, password=appPassword))
    # Get token
    data = post('users', expectJSON=False)
    token = get_token(data)
    # Assemble
    payload, countByKey = assemble(sqlalchemyURL)
    # Upload
    post('uploads', dict(token=token, payload=simplejson.dumps(payload)))
    # Logout
    post('users/logout')
    # Return
    return '\n'.join('%s: %s' % (key.capitalize(), count) for key, count in countByKey.iteritems())


def strip(text):
    return text.strip() if text else ''


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
        __table__ = tables['TECHNOL']
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
    print 'Loading companies...'
    companies = []
    for company in db.query(Company):
        companies.append((
            company.PRIMARYKEY,
            company.NAME))
    # Load contacts
    print 'Loading contacts...'
    contacts = []
    for contact in db.query(Contact):
        contacts.append((
            int(contact.PRIMARYKEY),
            strip(contact.FIRSTNAME),
            strip(contact.MIDDLEINI),
            strip(contact.LASTNAME),
            strip(contact.EMAIL),
        ))
    # Load countries
    print 'Loading countries...'
    countries = []
    for country in db.query(Country):
        countries.append((
            int(country.PRIMARYKEY),
            strip(country.NAME),
        ))
    # Load patents
    print 'Loading patents...'
    patents = []
    for patent in db.query(Patent):
        patents.append((
            int(patent.PRIMARYKEY),
            int(patent.TECHNOLFK),
            strip(patent.NAME),
            int(patent.LAWFIRMFK),
            strip(patent.LEGALREFNO),
            patent.FILEDATE.strftime('%Y%m%d') if patent.FIRSTNAME else '',
            int(patent.PATSTATFK),
            int(patent.PAPPTYPEFK),
            int(patent.COUNTRYFK)))
    # Load patentInventors
    print 'Loading patent inventors...'
    patentInventors = []
    for patentInventor in db.query(PatentInventor):
        patentInventors.append((
            int(patentInventor.PATENTSFK),
            int(patentInventor.CONTACTSFK),
            int(patentInventor.PI_ORDER)))
    # Load patentStatuses
    print 'Loading patent statuses...'
    patentStatuses = []
    for patentStatus in db.query(PatentStatus):
        patentStatuses.append((
            int(patentStatus.PRIMARYKEY),
            strip(patentStatus.NAME),
        ))
    # Load patentTypes
    print 'Loading patent types...'
    patentTypes = []
    for patentType in db.query(PatentType):
        patentTypes.append((
            int(patentType.PRIMARYKEY),
            strip(patentType.NAME),
        ))
    # Load phones
    print 'Loading phones...'
    phones = []
    for phone in db.query(Phone):
        phones.append((
            int(phone.PRIMARYKEY),
            int(phone.CONTACTSFK),
            strip(phone.PHONENUM),
            strip(phone.PHONETYPE),
        ))
    # Load technologies
    print 'Loading technologies...'
    technologies = []
    for technology in db.query(Technology):
        technologies.append((
            int(technology.PRIMARYKEY),
            strip(technology.TECHID),
            strip(technology.NAME),
        ))
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
