'Views for tracking patent activity'
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from tcd.models import db, Upload, Patent, PatentStatus, PatentType


def includeme(config):
    config.scan(__name__)
    config.add_route('patent_index', '')


@view_config(route_name='patent_index', renderer='patents/index.mak', permission='active')
def index(request):
    'Display patent activity'
    when_uploaded = db.query(Upload).order_by(Upload.when.desc()).first()
    patents = db.query(Patent).join(Patent.status, Patent.type).options(joinedload(
        Patent.technology, 
        Patent.firm, 
        Patent.status, 
        Patent.type, 
        Patent.inventors, 
        Patent.country,
    )).order_by(
        PatentStatus.name,
        PatentType.name,
        Patent.date_filed,
    ).all()
    return dict(when_uploaded=when_uploaded, patents=patents)
