<p>{{actions=get_actions(quest['qtype'], quest['status'], 'std', False)}}</p>
<p>{{for action in actions:}}
    {{=make_button(action,quest['id'])}}
    {{pass}}</p>




 




