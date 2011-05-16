'Views for processing uploads from remote sources'
import datetime
import simplejson
from pyramid.view import view_config

from tcd.libraries.tools import get_remote_ip
from tcd.models import db, Company, Contact, Country, Patent, PatentInventor, PatentStatus, PatentType, Phone, Technology, Upload


def includeme(config):
    config.scan(__name__)
    config.add_route('upload', 'uploads')


@view_config(route_name='upload', renderer='json', request_method='POST', permission='super')
def upload(request):
    'Process upload from remote source'
    params = request.params
    if params.get('token') != request.session.get_csrf_token():
        return dict(isOk=0, message='Invalid session token')
    # Unpack payload
    payload = params.get('payload')
    if not payload:
        return dict(isOk=0, message='Missing payload')
    try:
        payload = simplejson.loads(payload)
    except simplejson.JSONDecodeError:
        return dict(isOk=0, message='Could not load payload')
    try:
        companies = payload['companies']
        contacts = payload['contacts']
        countries = payload['countries']
        patents = payload['patents']
        patentInventors = payload['patentInventors']
        patentStatuses = payload['patentStatuses']
        patentTypes = payload['patentTypes']
        phones = payload['phones']
        technologies = payload['technologies']
    except KeyError, error:
        return dict(isOk=0, message='Missing key (%s)' % error)
    # Save
    for companyID, companyName in companies:
        db.merge(Company(
            id=int(companyID),
            name=companyName.strip(),
        ))
    for contactID, firstName, middleName, lastName, email in contacts:
        db.merge(Contact(
            id=int(contactID),
            name_first=firstName.strip(),
            name_middle=middleName.strip(),
            name_last=lastName.strip(),
            email=email.strip(),
        ))
    for countryID, countryName in countries:
        db.merge(Country(
            id=int(countryID),
            name=countryName.strip(),
        ))
    for patentID, technologyID, patentName, patentLawFirmID, patentLawFirmCase, patentFilingDate, patentStatusID, patentTypeID, countryID in patents:
        try:
            patentFilingDate = datetime.datetime.strptime(patentFilingDate, '%Y%m%d').date()
        except ValueError:
            patentFilingDate = None
        db.merge(Patent(
            id=int(patentID),
            technology_id=int(technologyID),
            name=patentName.strip(),
            firm_id=int(patentLawFirmID),
            firm_ref=patentLawFirmCase.strip(),
            date_filed=patentFilingDate,
            status_id=int(patentStatusID),
            type_id=int(patentTypeID),
            country_id=int(countryID),
        ))
    for patentID, contactID, piOrder in patentInventors:
        db.merge(PatentInventor(
            patent_id=int(patentID),
            contact_id=int(contactID),
            pi_order=int(piOrder),
        ))
    for patentStatusID, patentStatusName in patentStatuses:
        db.merge(PatentStatus(
            id=int(patentStatusID),
            name=patentStatusName.strip(),
        ))
    for patentTypeID, patentTypeName in patentTypes:
        db.merge(PatentType(
            id=int(patentTypeID),
            name=patentTypeName.strip(),
        ))
    for phoneID, contactID, phoneNumber, phoneType in phones:
        db.merge(Phone(
            id=int(phoneID),
            contact_id=int(contactID),
            number=phoneNumber.strip(),
            type=phoneType.strip(),
        ))
    for technologyID, technologyCase, technologyName in technologies:
        db.merge(Technology(
            id=int(technologyID),
            ref=technologyCase.strip(),
            name=technologyName.strip(),
        ))
    # Record
    db.add(Upload(
        ip=get_remote_ip(request),
        when=datetime.datetime.utcnow()))
    # Return
    return dict(isOk=1)
