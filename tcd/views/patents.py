'Views for tracking patent activity'
from pyramid.view import view_config
from sqlalchemy.orm import joinedload_all

from tcd.models import db, Upload, Contact, Patent, PatentInventor, PatentStatus, PatentType


def includeme(config):
    config.scan(__name__)
    config.add_route('patent_index', '')


@view_config(route_name='patent_index', renderer='patents/index.mak', permission='active')
def index(request):
    'Display patent activity'
    upload = db.query(Upload).order_by(Upload.when.desc()).first()
    patents = db.query(Patent).join(Patent.status, Patent.type).options(joinedload_all(
        Patent.technology, 
        Patent.firm, 
        Patent.status, 
        Patent.type, 
        Patent.inventors, 
        Patent.country,
        PatentInventor.contact
    )).order_by(
        PatentStatus.name,
        PatentType.name,
        Patent.date_filed,
    ).all()
    return dict(upload=upload, patents=patents)
