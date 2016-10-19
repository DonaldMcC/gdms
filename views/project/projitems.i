<div id="target"></div>


{{if auth.user_id == projectrow.proj_owner:}}
<h1>Draft Items for Project</h1>
<div id="questdraft">
    <script>
$("#questdraft").load("{{=URL('default', 'questload.load', args='projunlink', vars=dict(selection='QD',project=projectrow.id, project_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#QD').DataTable();} );
</script>

</div>
{{pass}}

<h1>Issues for Project</h1>
<div id="issueprog">
    <script>
$("#issueprog").load("{{=URL('default', 'questload.load', args='projunlink', vars=dict(selection='IP',project=projectrow.id, project_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#IP').DataTable();} );
</script>

</div>



<h1>Questions for Project</h1>
<div id="questprog">
    <script>
$("#questprog").load("{{=URL('default', 'questload.load', args='projunlink', vars=dict(selection='QP',project=projectrow.id, project_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#QP').DataTable();} );
</script>

</div>


<h1>Proposed Actions from Project</h1>
<div id="actionprog">
    <script>
$( "#actionprog" ).load("{{=URL('default', 'questload.load', args=['projunlink'],vars=dict(selection='AP', project=projectrow.id, project_filter=1, items_per_page=50, query='home', sortby='ResDate'))}}","test", function() {
  $('#AP').DataTable();} );
</script>
</div>


<h1>Resolved Issues</h1>
<div id="issueresolved">
    <script>
$("#issueresolved").load("{{=URL('default', 'questload.load', args='projunlink', vars=dict(selection='IR',project=projectrow.id, project_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#IR').DataTable();} );
</script>
</div>


<h1>Resolved Questions</h1>
<div id="questresolved">
    <script>
$( "#questresolved" ).load("{{=URL('default', 'questload.load', args=['projunlink'], vars=dict(selection='QR', project=projectrow.id, project_filter=1, items_per_page=50,sortby='ResDate'))}}","test", function() {
  $('#QR').DataTable();} );
</script>
</div>


<h1>Agreed Actions</h1>
<div id="actionresolved">
    <script>
$("#actionresolved" ).load("{{=URL('default', 'questload.load', args=['projunlink'],vars=dict(selection='AR', project=projectrow.id, project_filter=1, items_per_page=50, query='home', sortby='ResDate'))}}","test", function() {
  $('#AR').DataTable();} );
</script>
</div>
