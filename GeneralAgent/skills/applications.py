

def load_application_names(code_dir):
    """
    加载所有应用的名称
    """
    import os, json
    result = []
    for bot_name in os.listdir(code_dir):
        bot_dir = os.path.join(code_dir, bot_name)
        if os.path.isdir(bot_dir):
            bot_json_path = os.path.join(bot_dir, 'bot.json')
            if os.path.exists(bot_json_path):
                with open(bot_json_path, 'r') as f:
                    bot_json = json.load(f)
                    if 'icon' in bot_json:
                        bot_json['icon_url'] = os.path.join(code_dir, bot_name, bot_json['icon'])
                    bot_json['nickname'] = bot_json['name']
                    result.append(bot_json)
    return result



def load_application(code_path):
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