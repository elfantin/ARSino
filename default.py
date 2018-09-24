# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is the main controller of ARSino
# - index just redirects to domanda
# - domanda presents a question to the audience member
# - risposta is shown once the audience member has voted
# - consolle is used by the presenter to show results and set the next question
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def addmeta():
    response.title = "ARSino"
    response.meta.author = "Michele Pozzi"
    response.meta.description = T("A small and light Audience Response System")
    response.meta.keywords = "Audience Response System, presentation, quiz, multiple choice, MCQ, feedback"

# we cash the action and the view, so that we recalculate this only once every 5s
# after all everyone in the audience will get the same question
@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def index():
    request.requires_https()
    addmeta()
    response.subtitle = "Start Page"
    session.corrette = 0    # stores the questions correctly answered by user
    session.risposte = []   # will store questions already answered by user
    form=FORM('Session code:', INPUT(_name='session_code', requires=IS_IN_DB(db,'sessione.codice')), INPUT(_type='submit'))
    if form.validate():
        ses_id = db.sessione(codice = form.vars.session_code).id
        response.flash = T("Valid session received")
        redirect(URL('domanda/{}'.format(ses_id)))
    return dict(form=form)

# we cash the action and the view, so that we recalculate this only once every 5s
# after all everyone in the audience will get the same question
@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def domanda():
    request.requires_https()
    diz = {}
    addmeta()
    response.subtitle = "Question"
    ses_id = request.args[0]
    d = db((db.OdG.ses_id == ses_id) & (db.OdG.is_active == True)).select()
    try:
        dom_id = d[0].dom_id
    except:
        dom_id = 15 # Q15 says there are no questions...
    dom = db.domanda[dom_id]
    diz['illustra'] = dom.illustra
    diz['domanda'] = dom.testo
    diz['risposte'] = dom.scelte
    diz['bottoni'] = 'ABCDEFGH'  # letters of the buttons,must be longer than # of answers
    diz['dom_id'] = dom_id
    diz['ses_id'] = ses_id
    return response.render(diz)

def risposta():
    '''Page opened when response is submitted. Expects a compound url
risposta.html/ses_id/dom_id/ris_id
i.e. IDs of session/question/answer
'''
    request.requires_https()
    # expected url is risposta/
    addmeta()
    response.subtitle = "Responded"
    ses_id = request.args[0]
    dom_id = request.args[1]
    ris_id = 'ABCDEFGH'.find(request.args[2])
    diz = dict(domanda = db.domanda[dom_id].testo, 
               risposta = db.domanda[dom_id].scelte[ris_id],
               messaggio=T("Response received"))
    if not session.risposte:
        session.risposte = []
    if dom_id in session.risposte:
        #~ user has already answered this question
        diz['messaggio'] = T("You've already answered this question")
        return diz
    else:
        session.risposte.append(dom_id)
    if ris_id == db.domanda(dom_id).risposta - 1:
        session.corrette = (session.corrette or 0) + 1
    newrec = dict()
    newrec['ses_id'] = ses_id
    newrec['dom_id'] = dom_id
    newrec['ris_id'] = ris_id
    newrec['respondent_id'] = response.session_id
    db.risposte[0] = newrec # create new record in table
    return diz

@auth.requires_membership('presenter')
def consolle():
    """This is what the presenter looks at. It's used to select the next question and to show
the results of the previous.
"""
    addmeta()
    response.subtitle = "Presenter's Console"
    diz = dict()
    try:
        ses_id = request.args[0]
    except:
        max = db.OdG.ses_id.max()
        ses_id = db().select(max).first()[max] # set to latest session for which an OdG was created
    try:
        dom_id = request.args[1]
    except:
        rows = db(db.OdG.ses_id == ses_id).select()
        dom_id = rows[0].dom_id
    db(db.OdG.ses_id == ses_id).update(is_active = False)
    db((db.OdG.ses_id == ses_id) & (db.OdG.dom_id == dom_id)).update(is_active = True)
    dom_id_rows = db(db.OdG.ses_id == ses_id).select()
    diz['dom_id_rows'] = dom_id_rows # debug
    diz['domtesti'] = []
    diz['dom_ids'] = []
    for row in dom_id_rows:
        diz['domtesti'].append(db.domanda[row.dom_id].testo)
        diz['dom_ids'].append(db.domanda[row.dom_id].id)
    dom = db.domanda[dom_id]
    diz['dom_id'] = dom_id
    diz['ses_id'] = ses_id
    diz['session_code'] = db.sessione(id = ses_id).codice
    diz['domanda'] = dom.testo
    diz['risposte'] = dom.scelte
    diz['illustra'] = dom.illustra
    diz['bottoni'] = 'ABCDEFGH'  # letters of the buttons,must be longer than # of answers
    conta=[]
    for r in range(len(dom.scelte)):
        # how many made this response
        quanti = db((db.risposte.ses_id==ses_id) & (db.risposte.dom_id==dom_id) & (db.risposte.ris_id==r)).count()
        conta.append(quanti)
        # who gave the correct answer (if it existed)
        if (r+1)==db.domanda(dom_id).risposta:
            db((db.OdG.ses_id==ses_id) & (db.OdG.dom_id==dom_id)).update(n_correct = quanti)
    tot = 0
    for t in conta:
        tot += t
    db((db.OdG.ses_id==ses_id) & (db.OdG.dom_id==dom_id)).update(n_respond = tot)
    tt = tot or 1 # avoid div by zero
    diz['largo'] = [round(t*100.0/tt) for t in conta]
    diz['totale'] = tot
    domande = db(db.OdG.ses_id == ses_id).select()
    diz['domande'] = []
    diz['dom'] = []
    for d in domande:
        diz['domande'].append(db.domanda[d.dom_id].testo)
        diz['dom'].append(d.dom_id)
    return diz

#for large numbers of rows, using an iterator-based alternative has dramatically lower memory use:
#for row in db(db.table.id > 0).iterselect():
#    rtn = row
#     ses_id should be stored in the session or URI (of audience and presenter)
#     so that several presentation can happen at the same time
#     dom_id should be stored in a database, same as OdG, so that anyone
#     calling in with the right session gets offered the current question
#     dom_id = cache.ram('dom_id', lambda: -1, time_expire=None)
#     if dom_id == -1:
#         dom_id = 5; # should set to min Q available, 5 might have been deleted
#         cache.ram('dom_id', lambda: dom_id, time_expire=-1)
#     ses_id = cache.ram('ses_id', lambda: -1, time_expire=None)
#     if ses_id == -1:
#         ses_id = 1; # should set to min Q available, 5 might have been deleted
#         cache.ram('ses_id', lambda: ses_id, time_expire=-1)
    
# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
