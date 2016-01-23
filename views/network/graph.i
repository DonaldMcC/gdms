{{if debug == 'True':}}
    <div id="toolbox" class >
      <input type="file" id="hidden-file-upload"><input id="upload-input" type="image" title="upload graph" src="/nds/static/images/upload-icon.png" alt="upload graph">
        <input type="image" id="download-input" title="download graph" src="/nds/static/images/download-icon.png" alt="download graph">
        <input type="image" id="delete-graph" title="delete graph" src="/nds/static/images/trash-icon.png" alt="delete graph">
    </div>
        {{pass}}
    </div>
        <div>
        <INPUT TYPE=BUTTON id="redraw-graph", class="btn btn-primary btn-sm" onClick="" VALUE="RedrawD3">
		<INPUT TYPE=BUTTON id="editmode", class="pushme btn btn-primary btn-sm " onClick="" data-default-text="Click to Edit" data-new-text="Stop Editing" VALUE="Click to Edit">
        </div>

    <script>
        {{include 'network/graph.js'}}
    </script>