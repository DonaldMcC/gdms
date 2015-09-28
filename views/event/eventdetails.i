<h1>Event Details</h1>
<table id='TabAnswers' class='issuetable'>
<tbody>
<tr>
<th>Name</th>
<td>{{=eventrow.evt_name}}</td>
<td>Type</td>
<td>{{=eventrow.evt_shared and 'Shared'}}</td>
<td>Status</td>
<td>{{=eventrow.status}}</td>
</tr>
<tr>
<th>Description</th>
<td>{{=eventrow.description}}</td>
<td>Start Time</td>
<td>{{=eventrow.startdatetime}}</td>
</tr>
<tr>
<th>Location</th>
<td>{{#eventrow.locationid.location_name}}{{=eventrow.locationid}}</td>
<td>End Time</td>
<td>{{=eventrow.enddatetime}}</td>

</tr>
</tbody>
</table>
