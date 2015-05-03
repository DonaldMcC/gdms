#This will provide basic maintenance options on the main tables for now and
#also initial setup function to load the default template

def shape_mgmt():
    grid = SQLFORM.grid(db.shape_template, orderby=[db.shape_template.shape_prefix])
    return locals()

def shape_setup():
    #so lets go with define these but replace parameters with relevant points
    #posx, posy, stroke, fill, and text will do for now I think

#m 0 385  L20 385 Q440 400 500 -140  L350 -270 L200 -140 Q150 50 20 0 L0 0 z
#old left m 0 200  L180 200 Q480 100 400 -40  L300 -80 L200 -40 Q150 50 80 20 L0 20 z
#new right m 0 0 L0 385 L80 400 Q200 380 200 560  L350 680 L500 560 Q450 0 80 0 L0 0
#old right m 0 0 L0 350 L80 350 Q200 300 200 490  L325 580 L450 490 Q450 0 80 0 L0 0
    fwdjson = r'''new joint.shapes.basic.Path({
   id: '%s',
   position: { x: %d, y: %d },
   attrs: {
       path: { d: 'm 3 200  L153 200 L203 100 L153 0 L3 0 z ', stroke:'%s', fill: '%s' },
       text: { text: '%s', 'ref-y': .5, fill: 'white' }}})'''

    leftjson = r'''new joint.shapes.basic.Path({
           id: '%s',
   position: { x: %d, y: %d },
   attrs: {
       path: { d: 'm 0 485  L20 485 Q440 500 500 -40  L350 -170 L200 -40 Q150 110 20 100 L0 100 z ', stroke:'%s', fill: '%s'  },
       text: { text: '%s', 'ref-y': .5, fill: 'white' }}})'''

    rightjson = r'''new joint.shapes.basic.Path({
           id: '%s',
   position: { x: %d, y: %d },
   attrs: {
       path: { d: 'm 0 110 L0 495 L80 510 Q200 490 200 670  L350 790 L500 670 Q450 110 80 110 L0 110  ', stroke:'%s', fill: '%s' },
       text: { text: '%s', 'ref-y': .5, fill: 'white' }}})'''

    funcjson = r'''new joint.shapes.basic.Circle({
    id:'%s',
    size: { width: 70, height: 70 },
    position: {x: %d, y: %d},
    attrs: {circle: { stroke:'%s', fill: '%s', transform: 'translate(25, 25)' }, text: {text:'%s', fill:'white'}}})'''

    slotjson = r'''new joint.shapes.basic.Path({
           id: '%s',
                    position: { x: %d, y: %d },
                attrs: {
                path: { d: 'm0 0 L0 200 l10 0 q20 -100 0 -200 z', stroke:'%s', fill:'%s'  },
                    text: { text: '%s', 'ref-y': .5, fill: 'white' }}})'''

    linkjson = r'''new joint.dia.Link({
    id: '%s',
    source: { id: '%s' },
    target: { id: '%s' },
    attrs: ({
    '.connection': { stroke: 'blue', 'stroke-width': 5 },
    '.marker-target': { fill: 'yellow', d: 'M 10 0 L 0 5 L 10 10 z' }})})'''

    shapelist = [{'shape_type': 'Forward', 'shape_prefix': 'fwd', 'shape_json': fwdjson, 'description': 'The shape to move forward',
                'cub_action': 'This will be code' },
               {'shape_type': 'Left', 'shape_prefix': 'lft', 'shape_json': leftjson, 'description': 'The shape to move left',
                'cub_action': 'This will be code' },
               {'shape_type': 'Right', 'shape_prefix': 'rgt', 'shape_json': rightjson, 'description': 'The shape to move right',
                'cub_action': 'This will be code' },
               {'shape_type': 'Function', 'shape_prefix': 'fnc', 'shape_json': funcjson, 'description': 'The function shape',
                'cub_action': 'This will be code' },
               {'shape_type': 'Slot', 'shape_prefix': 'slt', 'shape_json': slotjson, 'description': 'The holes on the board',
                'cub_action': 'na'},
               {'shape_type': 'Link', 'shape_prefix': 'lnk', 'shape_json': linkjson, 'description': 'The links between slots',
                'cub_action': 'na'}]

    db.shape_template.truncate()
    db.commit

    for x in shapelist:
        db.shape_template.insert(**x)

    return locals()


def index():
    startupshapes = db(db.startup.id>0).select()
    cellsjson = '['
    slotarray = '['
    linkarray = '['
    palarray = '['

    for row in startupshapes:
        template=row.shape_template.shape_json % (row.shape_name, row.posx, row.posy,
                                                      row.stroke, row.fill,row.textstring)
        cellsjson += template + ','
        if row.shape_name[:3] == 'slt':
            slotarray += '"' + row.shape_name + '",'
        if row.shape_name[:3] == 'pal':
            palarray += '"' + row.shape_name + '",'

    startlinks = db(db.startlinks.id>0).select()
    for row in startlinks:
        template=row.shape_template.shape_json % (row.shape_name, row.sourceid, row.targetid)
        cellsjson += template + ','
        linkarray += '"' + row.shape_name + '",'


    cellsjson = cellsjson[:-1]+']'
    slotarray = slotarray[:-1]+']'
    linkarray = linkarray[:-1]+']'
    palarray = palarray[:-1]+']'
    return dict(cellsjson=XML(cellsjson), slotarray=XML(slotarray), linkarray=XML(linkarray), palarray=XML(palarray))

