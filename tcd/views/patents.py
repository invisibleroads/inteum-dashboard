'Views for tracking patent activity'
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, joinedload_all
from beaker.cache import cache_region

from tcd.models import db, Upload, Contact, Patent, PatentInventor, PatentStatus, PatentType, Phone


def includeme(config):
    config.scan(__name__)
    config.add_route('patent_index', '')


@view_config(route_name='patent_index', renderer='patents/index.mak', permission='active')
def index(request):
    'Display patent activity'
    upload = db.query(Upload).order_by(Upload.when.desc()).first()
    return dict(upload=upload, patents=get_patents())


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
