from social_core.pipeline.social_auth import associate_user as assoc_user
from social_core.pipeline.utils import partial_prepare
from functools import wraps
from gluon.globals import current
from utils import verifiable_redirect


#def partial(func):
#    @wraps(func)
#    def wrapper(strategy, pipeline_index, *args, **kwargs):
#        values = current.strategy.partial_save(pipeline_index, *args, **kwargs)
#        strategy.session_set('partial_pipeline', values)
#        return func(strategy, pipeline_index, *args, **kwargs)
#    return wrapper


def partial(func):
    """Wraps func to behave like a partial pipeline step, any output
    that's not None or {} will be considered a response object and
    will be returned to user.
    The pipeline function will receive a current_partial object, it
    contains the partial pipeline data and a token that is used to
    identify it when it's continued, this is useful to build links
    with the token.
    The default value for this parameter is partial_token, but can be
    overridden by SOCIAL_AUTH_PARTIAL_PIPELINE_TOKEN_NAME setting.
    The token is also stored in the session under the
    partial_pipeline_token key.
    """
    @wraps(func)
    def wrapper(strategy, backend, pipeline_index, *args, **kwargs):
        current_partial = partial_prepare(strategy, backend, pipeline_index,
                                          *args, **kwargs)

        out = func(strategy=strategy,
                   backend=backend,
                   pipeline_index=pipeline_index,
                   current_partial=current_partial,
                   *args, **kwargs) or {}

        if not isinstance(out, dict):
            strategy.storage.partial.store(current_partial)
            strategy.session_set('partial_pipeline_token',
                                 current_partial.token)
        return out
    return wrapper


def disconnect(strategy, entries, user_storage, on_disconnected=None,  *args, **kwargs):
    for entry in entries:
        user_storage.disconnect(entry, on_disconnected)


# changed from strategy as first parameter            
def associate_user(backend, uid, user=None, social=None, *args, **kwargs):
    assoc = assoc_user(backend, uid, user=user, social=social, *args, **kwargs)
    if assoc:
        providers = current.strategy.get_setting('SOCIAL_AUTH_PROVIDERS')
        #key = strategy.backend.name
        key = backend
        display_name = key in providers and providers[key]

        current.plugin_social_auth.session.flash = '%s %s' % \
                (current.plugin_social_auth.T('Added logon: '), display_name or key)
    return assoc

    
    
    
    
def clean_confirm_session(strategy, *args, **kwargs):
    if 'confirm' in strategy.session:
        del strategy.session.__confirm

@partial
def confirm_new_user(strategy, pipeline_index, user=None, *args, **kwargs):
    r = current.request

    if (not strategy.get_setting('SOCIAL_AUTH_CONFIRM_NEW_USER')) or 'confirmed' in r.args:
        return None

    # Save vars in session so we can keep them hidden
    strategy.session_set('confirm', r.vars)

    if user is None:
        return verifiable_redirect(f='user', args=['confirm'], vars={'backend': r.vars.backend})

