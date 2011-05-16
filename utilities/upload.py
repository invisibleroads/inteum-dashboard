'Command-line script to upload data'
import simplejson
from urllib import urlencode
from urllib2 import build_opener, HTTPCookieProcessor
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
    opener = build_opener(HTTPCookieProcessor())
    def post(relativeURL, valueByKey=None, expectJSON=True):
        url = appURL + '/' + relativeURL
        response = opener.open(url, urlencode(valueByKey or {}))
        data = response.read()
        response.close()
        if expectJSON:
            data = simplejson.loads(data)
            if options.verbose and not data.get('isOk'):
                return data.get('message')
        return data
    # Login
    showFeedback('Logging in...')
    post('users/login', dict(username=appUsername, password=appPassword))
    # Get token
    showFeedback('Getting token...')
    data = post('users', expectJSON=False)
    token = get_token(data)
    # Assemble
    showFeedback('Assembling payload...')
    payload, countByKey = assemble(sqlalchemyURL)
    # Upload
    showFeedback('Uploading...')
    post('uploads', dict(token=token, payload=simplejson.dumps(payload, encoding='latin-1')))
    # Logout
    showFeedback('Logging out...')
    post('users/logout')
    # Return
    return '\n'.join('%s: %s' % (key.capitalize(), count) for key, count in countByKey.iteritems())


def strip(text):
    return text.strip() if text else ''


def showFeedback(text):
    if 'options' not in dir() or options.verbose:
        print text


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
    showFeedback('Loading companies...')
    companies = []
    for company in db.query(Company):
        companies.append((
            company.PRIMARYKEY,
            company.NAME))
    # Load contacts
    showFeedback('Loading contacts...')
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
    showFeedback('Loading countries...')
    countries = []
    for country in db.query(Country):
        countries.append((
            int(country.PRIMARYKEY),
            strip(country.NAME),
        ))
    # Load patents
    showFeedback('Loading patents...')
    patents = []
    for patent in db.query(Patent):
        patents.append((
            int(patent.PRIMARYKEY),
            int(patent.TECHNOLFK),
            strip(patent.NAME),
            int(patent.LAWFIRMFK),
            strip(patent.LEGALREFNO),
            patent.FILEDATE.strftime('%Y%m%d') if patent.FILEDATE.year != 1899 else '',
            int(patent.PATSTATFK),
            int(patent.PAPPTYPEFK),
            int(patent.COUNTRYFK)))
    # Load patentInventors
    showFeedback('Loading patent inventors...')
    patentInventors = []
    for patentInventor in db.query(PatentInventor):
        patentInventors.append((
            int(patentInventor.PATENTSFK),
            int(patentInventor.CONTACTSFK),
            int(patentInventor.PI_ORDER)))
    # Load patentStatuses
    showFeedback('Loading patent statuses...')
    patentStatuses = []
    for patentStatus in db.query(PatentStatus):
        patentStatuses.append((
            int(patentStatus.PRIMARYKEY),
            strip(patentStatus.NAME),
        ))
    # Load patentTypes
    showFeedback('Loading patent types...')
    patentTypes = []
    for patentType in db.query(PatentType):
        patentTypes.append((
            int(patentType.PRIMARYKEY),
            strip(patentType.NAME),
        ))
    # Load phones
    showFeedback('Loading phones...')
    phones = []
    for phone in db.query(Phone):
        phones.append((
            int(phone.PRIMARYKEY),
            int(phone.CONTACTSFK),
            strip(phone.PHONENUM),
            strip(phone.PHONETYPE),
        ))
    # Load technologies
    showFeedback('Loading technologies...')
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
