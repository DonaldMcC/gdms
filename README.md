#Networked Decision Making
Networked Decision Making is software designed to radically disrupt the culture of meetings that currently pervades so many aspects of life.  While many tools have been developed to make meetings work better the tools available to eliminate the need for many meetings but still support consensual group decision making are few.  Meetings have a significant issue with scalability and we have an issue with this because it inevitably leads to a few people making decisions on behalf of many.

#Brief Abstract
This web application allows group decision making without meetings.  Issues, questions and actions are added to the system and then users can agree or disagree with issues, answer questions and approve actions.  The std process works on the basis that if 3 people consecutively and independently agree the answer to a question then they may well be correct. Items can also be prioritised and linked into a network of items. Groups can be used to restrict access to certain topics and users can also filter there activity by location and category.  Reasoning and discussion to support answers is encouraged and follow up questions and actions can also be submitted.  Resolved questions and actions can be challenged at which point they can go through the process again.

#Description of the Problem That Motivated Development of Networked Decision Making
Current group decision making methods are rather inefficient and unsatisfactory.  Voting is extremely costly and inefficient with the tendency to either consult everybody or nobody and meetings can also be extremely time consuming and really do not scale well beyond 15-20 people for a meaningful discussion and they are virtually always heavily influenced by a few key individuals and vested interests.

#Technical Description
Developed using web standards, python and the award wining web2py framework and best practices such as Model-View-Controller architecture, Separation of Concerns, and Don't Repeat Yourself.  Fast, intuitive UI featuring a custom application layout built using parts from Twitter Bootstrap, extensive AJAX and jQuery, .

#Secure
Can be deployed on any hardware or cloud platform and database that supports web2py

#Get Started
	* Install web2py on your preferred enivronment and configuration
	* Download and Install the Networked Decision Making package or
	* Clone   git clone https://github.com/nasa/isle.git
	* Start Web2py and point to the appropriate application url
	* Follow the setup instructions in the manual at https://www.penflip.com/donaldm2020/net-decision-making-manual

#Configuration
The configuration options are fully detailed in the manual.  You don't need any configuration to get started but for a production site you need to consider the database and log-on methods at a minimum.

#How to Contribute
There are some TODO items still showing in the code but new features should generally be proposed on the Networked Decision Making Site itself for approval.  The idea is that this software has the inbuilt mechanism to decide on it's own evolution.
Fork the project, make your changes, test, then submit a pull request. Submit any new bugs or feature requests to the issues page.

#Special Thanks To
* Web2py
* Python
* jQuery
* Bootstrap
* D3
* Datatables


