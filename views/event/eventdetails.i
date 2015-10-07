<h1>Event Details</h1>
<table id='TabAnswers' class='issuetable'>
<tbody>
<tr>
<th>Name</th>
<td>{{=eventrow.evt_name}}</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<th>Description</th>
<td>{{=eventrow.description}}</td>
<td class="pull-right">Start Time: </td>
<td>{{=eventrow.startdatetime.strftime('%a %d %b %Y %H:%M')}}</td>
<td class="pull-right">Status: </td>
<td>{{=eventrow.status}}</td>
</tr>
<tr>
<th>Location</th>
<td>{{=eventrow.locationid.location_name}}{{#eventrow.locationid}}</td>
<td class="pull-right">End Time: </td>
<td>{{=eventrow.enddatetime.strftime('%a %d %b %Y %H:%M')}}</td>
<td class="pull-right">Type: </td>
<td>{{=eventrow.evt_shared and 'Shared'}}</td>
</tr>
</tbody>
</table>
