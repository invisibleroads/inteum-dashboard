<%inherit file='/base.mak'/>

<%def name='title()'>Patents</%def>

<%def name='css()'>
table {border-collapse: collapse}
tr {height: 2em}
tr.even {background: #FBF5E6}
td {text-align: center}
.flag {color: darkblue}
.left {text-align: left}
.dataTables_filter {position: fixed; top: 0}
.dataTables_info {position: fixed; bottom: 0; left: 0}
#footer {position: fixed; bottom: 0; right: 0}
</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('tcd:static/dataTables/style.css')}">
<script src="${request.static_url('tcd:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('tcd:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
function computeTableHeight() {
	return $(window).height() - 110;
}
var table = $('#patents').dataTable({
	'aaSorting': [],
	'aoColumns': [
		{'sType': 'html'},
        {'sType': 'html'},
        {'sType': 'string'},
        {'sType': 'string'},
		{'sType': 'title-string'},
        {'sType': 'string'},
        {'sType': 'string'},
        {'sType': 'string'},
        {'sType': 'string'}
	],
	'bPaginate': false,
	'oLanguage': {'sSearch': 'Filter'},
	'sScrollX': '100%',
	'sScrollY': computeTableHeight()
});
$(window).bind('resize', function() {
	$('.dataTables_scrollBody').height(computeTableHeight());
	table.fnAdjustColumnSizing();
});
$('.dataTables_filter')
.append('&nbsp; ')
.append($('<input>', {
	id: 'download',
	type: 'button',
	value: 'Download',
	click: function() {
		var sortBys = $.map($('.sorting_asc, .sorting_desc'), function(n, i) {
			return $(n).text();
		});
		var patentIDs = $.map($('tr.patent'), function(n, i) {
			return getID(this);
		});
		var phrase = $('.dataTables_filter input:eq(0)').val();
		if (sortBys.length) {
			phrase += ' (sorted by ' + sortBys.join(', ').toLowerCase() + ')';
		}
		window.location = "${request.route_path('patent_download')}?ids=" + patentIDs.join(' ') + '&phrase=' + phrase;
	}
}))
.find('input:eq(0)').focus();
</%def>

<%!
import whenIO
%>

<table id=patents>
	<thead>
		<tr>
			<th>Case</th>
			<th>Inventor</th>
			<th>Status</th>
            <th>Type</th>
			<th>Filing Date</th>
			<th>Firm</th>
			<th class=left>Firm Ref</th>
			<th class=left>Country</th>
			<th class=left>Title</th>
		</tr>
	</thead>
	<tbody>
	% for patent in patents:
		<tr id=patent${patent.id} class=patent>
			<td>
				<span title='${patent.technology.name}'>${patent.technology.ref if patent.technology else ''}</span>
			</td>
			<td>
			% if patent.lead_contact:
				<%
				contact = patent.lead_contact
				%>
				<span title='${'%s\n%s' % (contact.email, '\n'.join('%s %s' % (phone.number, phone.type) for phone in contact.phones))}'>${contact.name_last}</span>
			% endif
			</td>
			<td>${patent.status.name if patent.status else ''}</td>
			<td>${patent.type.name if patent.type else ''}</td>
			<td>
			% if patent.date_filed:
				<span title="${patent.date_filed.strftime('%Y%m%d')}">${patent.date_filed.strftime('%m/%d/%y')}</span>
			% else:
				<span title=''></span>
			% endif
			</td>
			<td>${patent.firm.name if patent.firm else ''}</td>
			<td class=left>${patent.firm_ref}</td>
			<td class=left>${patent.country.name if patent.country else ''}</td>
			<td class=left>${patent.name}</td>
		</tr>
	% endfor
	</tbody>
</table>

<div id=footer>
% if upload:
Last updated: ${whenIO.WhenIO(USER_OFFSET).format(upload.when)}
% endif
</div>
