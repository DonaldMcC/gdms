<div>
<h1>Event Details</h1>
<table id='TabAnswers' class='issuetable'>
<tbody>
<tr>
<th width="10%">Name</th>
<th width="70%">{{=eventrow.evt_name}}</th>
<th width="10%" >Start</th>
<th width="10%">End</th>
</tr>
<tr>
<th>Description</th>
<td>{{=MARKMIN(eventrow.description)}}</td>
<td class="text-center">{{=eventrow.startdatetime.strftime('%a %d %b %Y %H:%M')}}</td>
<td class="text-center">{{=eventrow.enddatetime.strftime('%a %d %b %Y %H:%M')}}</td>
</tr>
<tr>
<th>Location</th>
<td>{{=eventrow.locationid}}</td>
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
</div>
