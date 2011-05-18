'Views for tracking patent activity'
import re
import csv
import datetime
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm import joinedload, joinedload_all
from beaker.cache import cache_region
from cStringIO import StringIO

from tcd.models import db, Upload, Contact, Patent, PatentInventor, PatentStatus, PatentType, Phone


def includeme(config):
    config.scan(__name__)
    config.add_route('patent_index', '')
    config.add_route('patent_download', 'patents/download')


@view_config(route_name='patent_index', renderer='patents/index.mak', permission='active')
def index(request):
    'Display patent activity'
    upload = db.query(Upload).order_by(Upload.when.desc()).first()
    patents = get_patents()
    return dict(upload=upload, patents=patents)


@view_config(route_name='patent_download', permission='active')
def download(request):
    'Return a spreadsheet of selected patents'
    # Load desired patents
    params = request.params
    phrase = params.get('phrase', '')
    patentIDs = params.get('ids', '').split()
    patentByID = dict((str(x.id), x) for x in get_patents())
    # Prepare CSV
    stringIO = StringIO()
    csvWriter = csv.writer(stringIO)
    csvWriter.writerow([
        'Case',
        'Lead Inventor',
        'Status',
        'Type',
        'Date Filed',
        'Firm',
        'Firm Ref',
        'Country',
        'Title',
    ])
    for patentID in patentIDs:
        try:
            patent = patentByID[patentID]
        except KeyError:
            continue
        contact = patent.lead_contact
        contactSummary = '%s\n%s\n%s' % (contact.name_last, contact.email, '\n'.join('%s %s' % (phone.number, phone.type) for phone in contact.phones)) if contact else ''
        csvWriter.writerow([
            patent.technology.ref if patent.technology else '',
            contactSummary,
            patent.status.name if patent.status else '',
            patent.type.name if patent.type else '',
            patent.date_filed.strftime('%m/%d/%y') if patent.date_filed else '',
            patent.firm.name if patent.firm else '',
            patent.firm_ref,
            patent.country.name if patent.country else '',
            patent.name,
        ])
    # Sanitize filename
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.() '
    phrase = re.sub(r'[^%s]' % alphabet, ' ', phrase) # Whitelist characters
    phrase = re.sub(r'\s+', ' ', phrase).strip() # Remove excess whitespace
    filename = '%s patents%s.csv' % (datetime.datetime.utcnow().strftime('%Y%m%d'), ' ' + phrase if phrase else '')
    # Generate
    stringIO.reset()
    body = stringIO.read()
    # Return
    return Response(body=body, content_length=len(body), content_disposition='attachment; filename="%s"' % filename)


@cache_region('long')
def get_patents():
    return db.query(Patent).join(Patent.status, Patent.type).options(
        joinedload(Patent.technology),
        joinedload(Patent.firm),
        joinedload(Patent.status),
        joinedload(Patent.type),
        joinedload_all(Patent.inventors, PatentInventor.contact, Contact.phones),
        joinedload(Patent.country),
    ).order_by(
        PatentStatus.name,
        PatentType.name,
        Patent.date_filed,
    ).all()
