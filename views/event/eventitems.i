<div id="target"></div>


{{if auth.user_id == eventrow.evt_owner:}}
<h1>Draft Items for event</h1>
<div id="questdraft">
    <script>
$("#questdraft").load("{{=URL('default', 'questload.load', args='evtunlink', vars=dict(selection='QD',event=eventid, event_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#QD').DataTable();} );
</script>

</div>
{{pass}}

<h1>Issues for event</h1>
<div id="issueprog">
    <script>
$("#issueprog").load("{{=URL('default', 'questload.load', args='evtunlink', vars=dict(selection='IP',event=eventid, event_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#IP').DataTable();} );
</script>

</div>



<h1>Questions for event</h1>
<div id="questprog">
    <script>
$("#questprog").load("{{=URL('default', 'questload.load', args='evtunlink', vars=dict(selection='QP',event=eventid, event_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#QP').DataTable();} );
</script>

</div>


<h1>Proposed Actions from event</h1>
<div id="actionprog">
    <script>
$( "#actionprog" ).load("{{=URL('default', 'questload.load', args=['evtunlink'],vars=dict(selection='AP', event=eventid, event_filter=1, items_per_page=50, query='home', sortby='ResDate'))}}","test", function() {
  $('#AP').DataTable();} );
</script>
</div>


<h1>Already Resolved Issues</h1>
<div id="issueresolved">
    <script>
$("#issueresolved").load("{{=URL('default', 'questload.load', args='evtunlink', vars=dict(selection='IR',event=eventid, event_filter=1, items_per_page=50, sortby='ResDate'))}}","test", function() {
  $('#IR').DataTable();} );
</script>
</div>


<h1>Already Resolved Questions</h1>
<div id="questresolved">
    <script>
$( "#questresolved" ).load("{{=URL('default', 'questload.load', args=['evtunlink'], vars=dict(selection='QR', event=eventid, event_filter=1, items_per_page=50,sortby='ResDate'))}}","test", function() {
  $('#QR').DataTable();} );
</script>
</div>


<h1>Already Agreed Actions</h1>
<div id="actionresolved">
    <script>
$("#actionresolved" ).load("{{=URL('default', 'questload.load', args=['evtunlink'],vars=dict(selection='AR', event=eventid, event_filter=1, items_per_page=50, query='home', sortby='ResDate'))}}","test", function() {
  $('#AR').DataTable();} );
</script>
</div>
