<div>
<h1>Project Details</h1>
<table id='TabAnswers' class='issuetable'>
<tbody>
<tr>
<th width="10%">Name</th>
<th width="70%">{{=projrow.proj_name}}</th>
<th width="10%" >Start</th>
<th width="10%">End</th>
</tr>
<tr>
<th>Description</th>
<td>{{=MARKMIN(projrow.description)}}</td>
<td class="text-center">{{=projrow.startdate.strftime('%a %d %b %Y')}}</td>
<td class="text-center">{{=projrow.enddate.strftime('%a %d %b %Y')}}</td>
</tr>
<tr>
<th>Status: </th>
<td id="projstatus">{{=projrow.proj_status}} and {{=projrow.proj_shared and 'Shared' or 'Not Shared'}}</td>
<td></td>
<td></td>
</tr>
</tbody>
</table>
</div>
