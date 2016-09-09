         <p>
<div class="input-group">         
 <INPUT TYPE=BUTTON id="help", class="btn btn-primary btn-warning btn-xs " onClick="" data-toggle =" popover"
        title ="In view mode you can drag items around the screen and shift click to create items, edit text or create directed links.
Use edit, link and add modes button to edit, link and create without using shift key eg on a touchscreen
Backspace or delete removes selected node from graph only and can remove links from database" data-content="" VALUE="Help">
             <INPUT TYPE=BUTTON id="key", class="btn btn-primary btn-success btn-xs " onClick="" data-toggle =" popover"
        title ="Issues: Blue
Questions: Green 
Actions: Yellow
Colour depth: priority
Resolved items have thicker border" data-content="" VALUE="Key">
<INPUT TYPE=BUTTON id="editmode", class="pushme btn btn-primary btn-xs " onClick="" data-default-text="Click to Edit" data-new-text="Stop Editing" VALUE="Click to Edit">

<div id="radioBtn" class="btn-group">
<a class="btn btn-primary btn-xs active" data-toggle="fun" data-title="V">View</a>
<a class="btn btn-primary btn-xs notActive" data-toggle="fun" data-title="E">Edit</a>
<a class="btn btn-primary btn-xs notActive" data-toggle="fun" data-title="L">Link</a>
<a class="btn btn-primary btn-xs notActive" data-toggle="fun" data-title="A">Add</a>
</div>
<input type="hidden" name="fun" id="fun">
</div>

</p>
    <div id="target"></div>
    <div id="message"></div>
    <div id="graph">

    {{if debug == 'True':}}
    <div id="toolbox" class >
      <input type="file" id="hidden-file-upload"><input id="upload-input" type="image" title="upload graph" src="/nds/static/images/upload-icon.png" alt="upload graph">
        <input type="image" id="download-input" title="download graph" src="/nds/static/images/download-icon.png" alt="download graph">
        <input type="image" id="delete-graph" title="delete graph" src="/nds/static/images/trash-icon.png" alt="delete graph">
    </div>
    {{pass}}
    </div>


<div id="map"></div>

