<h1>Event Details</h1>
<table id='TabAnswers' class='issuetable'>
<tbody>
<tr>
<th>Name</th>
<th>{{=eventrow.evt_name}}</th>
<th>Start</th>
<th>End</th>
</tr>
<tr>
<th>Description</th>
<td>{{=MARKMIN(eventrow.description)}}</td>
<td>{{=eventrow.startdatetime.strftime('%a %d %b %Y %H:%M')}}</td>
<td>{{=eventrow.enddatetime.strftime('%a %d %b %Y %H:%M')}}</td>
</tr>
<tr>
<th>Location</th>
<td>{{=eventrow.locationid.location_name}}{{#eventrow.locationid}}</td>
<td></td>
<td></td>
</tr>
<th>Status: </th>
<td>{{=eventrow.status}} and {{=eventrow.evt_shared and 'Shared' or 'Not Shared'}}</td>
<td></td>
<td></td>
</tr>
</tbody>
</table>
