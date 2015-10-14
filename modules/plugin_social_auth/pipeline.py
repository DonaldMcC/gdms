from plugin_social_auth.social.pipeline.social_auth import associate_user as assoc_user
from functools import wraps
from gluon.globals import current
from utils import verifiable_redirect

def partial(func):
    @wraps(func)
    def wrapper(strategy, pipeline_index, *args, **kwargs):
        values = strategy.partial_to_session(pipeline_index, *args, **kwargs)
        strategy.session_set('partial_pipeline', values)
        return func(strategy, pipeline_index, *args, **kwargs)
    return wrapper

def disconnect(strategy, entries, user_storage, on_disconnected=None,  *args, **kwargs):
    for entry in entries:
        user_storage.disconnect(entry, on_disconnected)

def associate_user(strategy, uid, user=None, social=None, *args, **kwargs):
    assoc = assoc_user(strategy, uid, user=user, social=social, *args, **kwargs)
    if assoc:
        providers = strategy.get_setting('SOCIAL_AUTH_PROVIDERS')
        key = strategy.backend.name
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

