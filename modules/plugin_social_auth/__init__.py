import sys, os

# Allow importing of the wrapped python-social-auth module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#FIXME: Hack to social.utils.import_module() work
from plugin_social_auth import w2p_strategy, models, utils, pipeline
sys.modules['plugin_social_auth.w2p_strategy'] = w2p_strategy
sys.modules['plugin_social_auth.models'] = models
sys.modules['plugin_social_auth.utils'] = utils
sys.modules['plugin_social_auth.pipeline'] = pipeline
