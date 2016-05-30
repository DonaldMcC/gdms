
{{if groupcount:}}
{{grouptots=[0,0,0,0,0,0]}}
{{totalkeys=[1,2,7,8,13,14]}}
<table id='QuestCount' class='table table-bordered table-condensed'>
				<thead>
					<tr>
                        <th>Group</th>
						<th>Issue in prog</th>
                        <th>Agreed Issue</th>
                        <th>Quest in prog</th>
                        <th>Resolved Quest</th>
                        <th>Action in Prog</th>
                         <th>Agreed Action</th>
                    </tr>
                </thead>
                    <tbody>
{{for i,row in enumerate(groupcount):}}
<tr class="grouprow collapse">
<td>{{=A(row.groupcatname,_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'all'],extension='html'))}}</td>
<td>{{=A(row.questcounts[1],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'issue','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[2],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'issue','Agreed'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[7],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'quest','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[8],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'quest','Resolved'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[13],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'action','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[14],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'action','Agreed'],extension='html'))}}</td>
</tr>
{{for x in range(6):}}
{{grouptots[x] += row.questcounts[totalkeys[x]]}}
{{pass}}
{{pass}}
<tr>
<td>{{=A(SPAN(_class='glyphicon glyphicon-plus',_id="GroupTotSpan"),'Group Total',_id="GroupTot")}}</td>
<td>{{=A(grouptots[0],_href=URL('review','newlist',args=['G','Total','issue','InProg'],extension='html'))}}</td>
    <td>{{=A(grouptots[1],_href=URL('review','newlist',args=['G','Total','issue','Agreed'],extension='html'))}}</td>
    <td>{{=A(grouptots[2],_href=URL('review','newlist',args=['G','Total','quest','InProg'],extension='html'))}}</td>
    <td>{{=A(grouptots[3],_href=URL('review','newlist',args=['G','Total','quest','Resolved'],extension='html'))}}</td>
    <td>{{=A(grouptots[4],_href=URL('review','newlist',args=['G','Total','action','InProg'],extension='html'))}}</td>
    <td>{{=A(grouptots[5],_href=URL('review','newlist',args=['G','Total','action','Agreed'],extension='html'))}}</td>
</tr>
{{cattots=[0,0,0,0,0,0]}}
{{totalkeys=[1,2,7,8,13,14]}}
{{for i,row in enumerate(categorycount):}}
<tr class="catrow collapse">
<td>{{=A(row.groupcatname,_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'all'],extension='html'))}}</td>
<td>{{=A(row.questcounts[1],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'issue','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[2],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'issue','Agreed'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[7],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'quest','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[8],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'quest','Resolved'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[13],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'action','InProg'],extension='html'))}}</td>
    <td>{{=A(row.questcounts[14],_href=URL('review','newlist',args=[row.groupcat,row.groupcatname,'action','Agreed'],extension='html'))}}</td>
</tr>
{{for x in range(6):}}
{{cattots[x] += row.questcounts[totalkeys[x]]}}
{{pass}}
{{pass}}
<tr>
<td>{{=A(SPAN(_class='glyphicon glyphicon-plus',_id="CatTotSpan"),'Category Total',_id="CatTot")}}</td>
<td>{{=A(cattots[0],_href=URL('review','newlist',args=['C','Total','issue','InProg'],extension='html'))}}</td>
    <td>{{=A(cattots[1],_href=URL('review','newlist',args=['C','Total','issue','Agreed'],extension='html'))}}</td>
    <td>{{=A(cattots[2],_href=URL('review','newlist',args=['C','Total','quest','InProg'],extension='html'))}}</td>
    <td>{{=A(cattots[3],_href=URL('review','newlist',args=['C','Total','quest','Resolved'],extension='html'))}}</td>
    <td>{{=A(cattots[4],_href=URL('review','newlist',args=['C','Total','action','InProg'],extension='html'))}}</td>
    <td>{{=A(cattots[5],_href=URL('review','newlist',args=['C','Total','action','Agreed'],extension='html'))}}</td>
</tr>
</tbody>
</table>

{{else:}}
<p>No items</p>
{{pass}}

<script>
{{include 'default/questcountload.js'}}
</script>
