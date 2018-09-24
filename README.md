# ARSino
A small, and cute, Audience Response System powered by web2py and python3
Check out a little demo site at https://arsino.pythonanywhere.com/. The presenter's console, used to activate the questions is at https://arsino.pythonanywhere.com/consolle (read below for login details).

## DISCLAIMER. 
A bigger disclaimer than usual: I am NOT a coder, I can just write some code. The code will not be elegant and may still be buggy. I wrote it because I needed an ARS for my lectures, and I also had a limited time to develop it. However, it's been used in real life scenarios, with about one hundred university students per session, and it has worked well.

## Installation
ARSino has been developed as a web app of [web2py](http://web2py.com/). Both are written in python. You need a webserver running web2py to use ARSino, luckily it is easy to get this with [pythonanywhere.com](https://www.pythonanywhere.com). It is a great service that can be used to practise python, web frameworks etc. 

All the files specific to ARSino are available above for inspection. It is however recommended to use the web2py app package to install ARSino on a web server previously prepared with web2py. 

Once you have a running installation of web2py (tested on v. 2.14.6), go to the web2py administrative interface, where all the apps are visible. On the right panel, work on the **Upload and install packed application** section to upload the ARSino.w2p\* file you can download from the list above. For more information, please refer to the [web2py documentation](http://web2py.com/init/default/documentation).

\* this is a gzipped tar archive

ARSino has one default privileged user: the presenter. The login name is The-Presenter@example.com, with a default password of *arsino*. You can (i.e. should) edit name, email address and password by editing the record in the database table *db.auth_user*, using standard web2py methods (see below for a bit more info).

## Usage

### The presenter's console
The presenter's console is optimised for display on a large screen typically with a projector. A resolutions of HD or Full HD works best. It is typically found at `/consolle` or `/ARSino/default/consolle` if the web app is called ARSino and is not the [default app](http://web2py.com/book/default/chapter/04#Application-init). 

![The Presenter's Console](https://github.com/elfantin/ARSino/blob/master/ConsollePiezo.png)

The console is used to activate the questions and show the results. Typically the presenter would select the question with the dropdown (which is always populated with all the questions for that session). Once selected, the question is shown. The audience would then be asked to answer it on their own devices. The presenter can, at any time, refresh the page to update the results (for best results, give a specified amount of time to the audience and refresh only once or twice after it has elapsed).

### The audience interface
When the audience visits the website they are presented with a welcome screen where they have to insert the session code, previously given by the presenter (if the app is called ARSino and is not the default one, they'd visit `http://example.com/ARSino/`). Once the session code is submitted, the active question is shown. The audience interface is optimised for mobile devices. When they touch on one of the answer-buttons, the page reloads showing the question and the answer given. On the same page, a button triggers a page reload to be used when the presenter moves on to the next question.

The three main pages seen by the audience are:

Login | Answer | Confirmation
----- | ------ | ------------
![login](https://github.com/elfantin/ARSino/blob/master/Audience_Login.png) | ![answer](https://github.com/elfantin/ARSino/blob/master/Audience_Question.png) | ![Confirmation](https://github.com/elfantin/ARSino/blob/master/Audience_Confirm.png)

### General database editing
web2py offers a built-in powerful way to manage databases, hence it was not necessary to create custom code for this. From the design page of web2py (e.g. `/admin/default/design/ARSino`), one gets an overview of the whole web app and can edit, among many other things and files, also the database. By clicking the *database administration* button under **Models**, a list of tables is presented and a new records can be added simply by clicking the button *NEW RECORD* on the right of the table name. The fields have a short explanation which helps in their completion.

### Creating questions
As mentioned above, by clicking the *database administration* button under **Models**, a list of tables is presented and a new question can be added simply by clicking the button *NEW RECORD* on the right of the db.domanda link. In general one should try to keep questions and answers rather short, or the layout may suffer. It is possible to add one image to the question.

### Creating a session
The table *sessione* holds brief info about the presentation/lecture. The most important field is the session code, which will have to be given to the audience when they open the interface dedicated to them.

### Creating an agenda
Once the questions and the session are created, it is necessary to indicate which of those questions will be used in each presentation/lecture session. This permits the re-use of questions in different sessions. This information is held in the OdG table. Only the first three fields need filling. The first is the human readable session code and the second is the question itself. Both are answered via a dropdown (not sure if this will get awkward with hundreds of questions or questions that are too long). The third field is a check box, indicating the question that is active at any given moment in the session; this means that only one question should be active in each session. A dropdown in the presenter's console permits to select the active question or deactivate all questions in the session. This is achieved internally setting/resetting this flag. A feedback page is presented to the each respondent if no questions are active in the session he logged into. 

## Internals (i.e. some technical details)
### Database

ARSino exploits the power of database handling offered by web2py. There are several tables defined in the database, some are standard for a web2py installation and include users, permissions, groups, etc. The tables specific for ARSino are 4:
- *domanda*: this contains all the questions ever created, including the set of answers presented and the correct answer. It is possible to add one image to each question, the link to which will be stored in this table.
- *sessione*: this table contains the presentation sessions. The fields are a unique human-friendly code (e.g. using the date as MMDD), the actual date of the session and a brief description.
- *OdG*: this is the agenda for the day and relates the two prevous tables, therefore storing which questions will be available in each presentation session
- *risposte*: this is the most populated table as it will store all the answers from the audience. Its fields are the session ID and the question ID, the identifier of the respondent and the answer given (just an integer). The identifier is randomly generated by web2py, although it contains the IP address of the client: the objective is not to identify the respondent but only telling them apart, e.g. to provide feedback and prevent double answers. This table should not be edited manually, except to delete old entries to save space.

### Cookies
It is essential that the audience have their browser set to accept cookies: ARSino keeps track of each user to be able to provide end-of-session feedback and prevent double-answers. If cookies are not enabled, the users will not be able to get to the questions, being permanently stuck to the login page and asked to enter the session code.

### Languages
web2py handles different languages, however that was not needed for my purpose and the feature is not used.
