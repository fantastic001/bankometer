
def load_config():
    """
    Loads YAML config from default path (~/.config/bankometer_config.yml) or from path specified in BANKOMETER_CONFIG environment variable.
    """
    import os
    import yaml
    config_path = os.path.expanduser("~/.config/bankometer_config.yml")
    if "BANKOMETER_CONFIG" in os.environ:
        config_path = os.environ["BANKOMETER_CONFIG"]
    with open(config_path, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

class BankInterface:
    def __init__(self, config):
        self.config = config
    
    def get_config(self, name, default=None):
        return self.config.get(name, default)
    
    def get_balance(self):
        raise NotImplementedError()
    def get_transactions(self):
        raise NotImplementedError()
    def login(self):
        raise NotImplementedError()

def load_bank_module(config, account_name) -> BankInterface:
    """
    Dynamically imports module and loads class inheriting BankInterface.

    This function will instantiate object of the class and pass config part for specified account.
    """
    config = config["accounts"][account_name]
    import importlib
    modulename = config["module"].split(".")[0]
    classname = config["module"].split(".")[1]
    module = importlib.import_module("bankometer.bank_modules.%s" % modulename)
    return getattr(module, classname)(config)

