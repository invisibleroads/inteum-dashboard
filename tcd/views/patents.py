'Views for tracking patent activity'
import csv
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
    params = request.params
    patentIDs = params.get('ids', [])
    patents = get_patents()
    stringIO = StringIO()


    stringIO.reset()
    body = stringIO.read()
    return Response(
        body=body,
        content_length=len(body),
        content_disposition='attachment; filename="patents.csv"')


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
