from plugin_social_auth.utils import strategy, get_current_user, login_user, process_exception
from social.actions import do_complete


@strategy(URL('plugin_social_auth', 'complete'))
def complete():
    # Store "next" value in session
    _next = current.request.vars.get('next', None)

    if _next:
        current.strategy.session_set('next', _next)

    try:
        return do_complete(current.strategy,
                           login=lambda strat, user, social_user: login_user(user.row),
                           user=get_current_user())
    except Exception as e:
        process_exception(e)


def user():
    return auth()


def index():
    # Redirect to app index url if it's configured
    index_url = plugins.social_auth.get('SOCIAL_AUTH_APP_INDEX_URL', None)
    if index_url:
        redirect(index_url)
