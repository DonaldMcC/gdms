{{from ndsfunctions import truncquest}}

{{if resolved:}}
<h1>Resolved Items</h1>
<table id='Resitems' class='table issuetable2 table-bordered table-condensed'>
				<thead>
					<tr>
						<th width="5%">Type</th>
                        <th width="55%">Item Text</th>
                        <th width="15%">Answer</th>
                        <th width="8%"># Agree</th>
                        <th width="8%"># Disagree</th>
                        <th width="9%">Resolved</th>
                    </tr>
                </thead>
                    <tbody>
{{for i,row in enumerate(resolved):}}
<tr class={{if row.status == 'In Progress':}}"inprog"{{else:}}"resolved"{{pass}}>
<th><a href="{{=URL('viewquest','index',args=[row.id])}}">{{=row.qtype}}</a></th>
<td>{{=truncquest(row.questiontext)}}</td>
<td>{{=row.correctanstext()}}</td>
<td>{{=row.othercounts[3]}}</td>
<td>{{=row.othercounts[4]}}</td>
<td>{{=prettydate(row.resolvedate)}}</td>
</tr>
{{pass}}
 </tbody>
</table>
{{else:}}
<h3>No items resolved in the period.</h3>
{{pass}}

<h1>Items Submitted</h1>
{{if submitted:}}
<table id='TabActions' class='table issuetable2 table-bordered table-condensed'>
				<thead>
					<tr>
						<th width="5%">Type</th>
                        <th width="60%">Item Text</th>
                        <th width="13%">Scope</th>
                        <th width="12%">Category</th>
                        <th width="10%">Status</th>
                    </tr>
                </thead>
                    <tbody>
{{for row in submitted:}}
<tr class={{if row.status == 'In Progress':}}"inprog"{{else:}}"resolved"{{pass}}>
<th><a title="{{=row.status}}" href="{{=URL('viewquest','index',args=[row.id])}}">{{=row.qtype}}</a></th>
<td>{{=truncquest(row.questiontext)}}</td>
<td>{{=row.scopetext}}</td>
<td>{{=row.category}}</td>
<td>{{=row.status}}</td>
</tr>
{{pass}}
 </tbody>
</table>
{{else:}}
<p>No items submitted in the period.</p>
{{pass}}


{{if challenged:}}
<h1>Challenged Items</h1>
<table id='Challquestions' class='table issuetable2 table-bordered table-condensed'>
				<thead>
					<tr>
						<th width="5%">Level</th>
                        <th width="55%">Question</th>
                        <th width="15%">Answer</th>
                        <th width="8%"># Agree</th>
                        <th width="8%"># Disagree</th>
                        <th width="9%">Challenged</th>
                    </tr>
                </thead>
                    <tbody>
{{for i,row in enumerate(challenged):}}
<tr class={{if row.status == 'In Progress':}}"inprog"{{else:}}"resolved"{{pass}}>
<th><a href="{{=URL('viewquest','index',args=[row.id])}}">{{=row.question_level}}</a></th>
<td>{{=truncquest(row.questiontext)}}</td>
<td>{{=row.correctanstext()}}</td>
<td>{{=row.othercounts[3]}}</td>
<td>{{=row.othercounts[4]}}</td>
<td>{{=row.challengedate}}</td>
</tr>
{{pass}}
 </tbody>
</table>
{{else:}}
<h3>No items challenged in the period.</h3>
{{pass}}
