{{if qtype=='deleted':}}
<h1>{{=item.capitalize()}} deleted</h1>
          {{else:}}
<h1>{{=item.capitalize()}} submitted</h1>

<p>Thanks for submitting your {{=item}}.
    {{if status=='Resolved':}}As this is a self resolved question you can now linke to follow-items to more fully document your chain of thought. </p>
    {{elif status!='Draft':}}It will now be sent out for answering or approval in accordance with the process explained <a href="{{=URL('about','index')}}">here</a> </p>
{{else:}}
<p>As this is a draft question it will not be sent out until you update via the my drafts menu and finalise and set the status to in progress.  At that point the question can no longer be edited. </p>
{{pass}}
    {{if status!='Resolved':}}
<p>You are awarded points for submitting items (issues, questions and actions) - however these only get credited to your score once the question has been resolved or the action has been agreed.
    Items that are more difficult and take longer to resolve are awarded more points.  However they need to be considered both urgent and important to get priority within the system.  You do not get any points for submitting an action unless it is approved.</p>
{{pass}}
<h2>Follow on questions and actions</h2>
<p>You can submit a follow on item (issue, question or action). You can also create links between items and these can be seen using the show as network button which is available at various points on the site. </p>

 <p>
 {{=get_buttons(quest['qtype'], quest['status'], quest['resolvemethod'], quest['id'], quest['auth_userid'], auth.user_id, False, 'Submit')}}
 </p>

{{pass}}