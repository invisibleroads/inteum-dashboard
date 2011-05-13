'Views for processing uploads from remote sources'
import datetime
import simplejson
from pyramid.view import view_config

from tcd.libraries.tools import get_remote_ip
from tcd.models import db, Patent, PatentType, PatentStatus


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
        patents = payload['patents']
        patentTypes = payload['patentTypes']
        patentStatuses = payload['patentStatuses']
    except KeyError, error:
        return dict(isOk=0, message='Missing key (%s)' % error)
    # Save
    for patentStatusID, text in patentStatuses:
        db.merge(PatentStatus(
            id=int(patentStatusID),
            text=text.decode('utf-8')))
    for patentTypeID, text in patentTypeID:
        db.merge(PatentType(
            id=int(patentTypeID),
            text=text.decode('utf-8')))
    for patentID, patentFilingDateInSecondsFromEpoch, patentTypeID, patentStatusID in patents:
        db.merge(Patent(
            id=patentID,
            date_filed=datetime.datetime.utcfromtimestamp(float(patentFilingDateInSecondsFromEpoch)).date(),
            type_id=int(patentTypeID),
            status_id=int(patentStatusID)))
    # Record
    db.add(Upload(
        ip=get_remote_ip(request),
        when=datetime.datetime.utcnow()))
    # Return
    return dict(isOk=1)
