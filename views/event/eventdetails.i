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
<td>{{=eventrow.description}}</td>
<td class="text-center">{{=eventrow.startdatetime.strftime('%a %d %b %Y %H:%M')}}</td>
<td class="text-center">{{=eventrow.enddatetime.strftime('%a %d %b %Y %H:%M')}}</td>
</tr>
<tr>
<th>Location</th>
<td>{{=MARKMIN(eventrow.locationid.location_name)}}</td>
<td></td>
<td></td>
</tr>
<tr>
<th>Status: </th>
<td>{{=eventrow.status}} and {{=eventrow.evt_shared and 'Shared' or 'Not Shared'}}</td>
<td></td>
<td></td>
</tr>
</tbody>
</table>
