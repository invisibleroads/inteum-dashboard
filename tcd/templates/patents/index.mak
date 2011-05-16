<%inherit file='/base.mak'/>

<%def name='title()'>Patents</%def>

<%def name='css()'>
td {text-align: center}
.flag {color: darkblue}
</%def>

<%def name='toolbar()'>
% if when_uploaded:
Last updated: ${whenIO.WhenIO(USER_OFFSET).format(when_uploaded)}
% endif
</%def>

<%def name='root()'>
<link rel=stylesheet href="${request.static_url('tcd:static/dataTables/style.css')}">
<script src="${request.static_url('tcd:static/dataTables/jquery.dataTables.min.js')}"></script>
<script src="${request.static_url('tcd:static/dataTables/jquery.dataTables.titleString.min.js')}"></script>
</%def>

<%def name='js()'>
function computeTableHeight() {
	return $(window).height() - 100;
}
var table = $('#patents').dataTable({
	'aaSorting': [
		[0, 'asc']
		[1, 'asc']
		[2, 'asc']
	],
	'aoColumns': [
		{'sType': 'html'},
        {'sType': 'html'},
		{'sType': 'title-string'}
	],
	'bInfo': false,
	'bPaginate': false,
	'oLanguage': {'sSearch': 'Filter'},
	'sScrollY': computeTableHeight()
});
$(window).bind('resize', function() {
	$('.dataTables_scrollBody').height(computeTableHeight());
	table.fnAdjustColumnSizing();
});
$('.dataTables_filter input').focus();
</%def>

<%!
import whenIO
%>

<table id=patents>
	<thead>
		<tr>
			<th>Case</th>
			<th>Inventor</th>
			<th>Name</th>
			<th>Status</th>
            <th>Type</th>
			<th>Filing Date</th>
			<th>Firm</th>
			<th>Firm Ref</th>
			<th>Country</th>
		</tr>
	</thead>
	<tbody>
	% for patent in patents:
		<tr id=patent${patent.id} class=patent>
			<td>${patent.technology.ref if patent.technology else ''}</td>
			<td>${sorted(patent.inventors, key=lambda x: x.pi_order)[0].name_last if patent.inventors else ''}</td>
			<td>${patent.name}</td>
			<td>${patent.status.name if patent.status else ''}</td>
			<td>${patent.type.name if patent.type else ''}</td>
			<td>
				<span title="${patent.date_filed.strftime('%Y%m%d')}">
					${patent.date_filed.strftime('%B %d, %Y')}
				</span>
			</td>
			<td>${patent.firm.name}</td>
			<td>${patent.firm_ref}</td>
			<td>${patent.country.name}</td>
		</tr>
	% endfor
	</tbody>
</table>
