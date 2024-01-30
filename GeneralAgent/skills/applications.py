
def load_applications():
    """
    load all applications(bots) metadata
    """
    from GeneralAgent.utils import get_applications_dir
    local_bots = _load_bots(_get_local_applications_dir())
    remote_bots=  _load_bots(get_applications_dir())
    for bot in remote_bots:
        bot['nickname'] = '# ' + bot['nickname']
    return local_bots + remote_bots


def _get_local_applications_dir():
    from GeneralAgent.utils import get_local_applications_dir
    return get_local_applications_dir()


def _load_bots(code_dir):
    import os, json
    result = []
    for bot_name in os.listdir(code_dir):
        bot_dir = os.path.join(code_dir, bot_name)
        if os.path.isdir(bot_dir):
            result.append(_load_bot_metadata(bot_dir))
    return result


def _load_bot_metadata(bot_dir):
    import os, json
    bot_json_path = os.path.join(bot_dir, 'bot.json')
    if os.path.exists(bot_json_path):
        with open(bot_json_path, 'r', encoding='utf-8') as f:
            bot_json = json.load(f)
            # if 'icon' in bot_json:
            #     bot_json['icon_url'] = os.path.join(bot_dir, bot_json['icon'])
            # if 'js_path' in bot_json:
            #     bot_json['js_path'] = os.path.join(bot_dir, bot_json['js_path'])
            bot_json['nickname'] = bot_json['name']
            return bot_json
    return None


def load_bot_metadata_by_id(bot_id):
    """
    load bot metadata by bot id
    """
    import os
    local_dir = _get_local_applications_dir()
    from GeneralAgent.utils import get_applications_dir
    remote_dir = get_applications_dir()
    bot_dir = os.path.join(local_dir, bot_id)
    if not os.path.exists(bot_dir):
        bot_dir = os.path.join(remote_dir, bot_id)
    return _load_bot_metadata(bot_dir)


def get_application_module(bot_id):
    """
    get application module by bot id
    """
    import os
    from GeneralAgent.utils import get_applications_dir
    local_dir = _get_local_applications_dir()
    remote_dir = get_applications_dir()
    code_path = os.path.join(local_dir, f"{bot_id}/main.py")
    if not os.path.exists(code_path):
        code_path = os.path.join(remote_dir, f"{bot_id}/main.py")
    return _load_application(code_path)

def get_application_dir(bot_id):
    """
    get application dir by bot id
    """
    import os
    from GeneralAgent.utils import get_applications_dir
    local_dir = _get_local_applications_dir()
    remote_dir = get_applications_dir()
    code_dir = os.path.join(local_dir, f"{bot_id}")
    if not os.path.exists(code_dir):
        code_dir = os.path.join(remote_dir, f"{bot_id}")
    return code_dir


def _load_application(code_path):
    """
    load application with code path
    """
    import os, importlib.util, logging
    application = None
    try:
        spec = importlib.util.spec_from_file_location("main", code_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        application = module
    except Exception as e:
        logging.exception(e)
    return application