

# Introduction 

Bankometer is a tool for managing your bank accounts 

# Bankometer Configuration and Usage Guide


In order to get configuration parameters you can modify, execute:

    python scripts/detect_function_calls.py  bankometer/ get_config_ --exclude get_config_location

Every configuration parameter can be changed in configuration file and overwritten by using 
environment variable. 

For instance, `url` can be specified in configuration file and can be modified using `BANKOMETER_URL` environment variable. 

Configuration file is specified using `BANKOMETER_CONFIG` and default location is at `~/.config/bankometer.json`


# Configuration reference 

| param              | type   | default                                                                                                                                                                                                                                                                      | doc                                  |
|:-------------------|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------|
| plugin_search_path | list   | ["'/usr/local/share/' + PROJECT_NAME + '/plugins'", "'/usr/share/' + PROJECT_NAME + '/plugins'", "os.path.join(os.path.expanduser('~'), '.' + PROJECT_NAME, 'plugins')", "os.path.join(os.path.expanduser('~'), '.local', 'share', PROJECT_NAME, 'plugins')", 'os.getcwd()'] | List of plugin search paths          |
| disabled_plugins   | list   | []                                                                                                                                                                                                                                                                           | List of plugins to disable           |
| plugins            | list   | []                                                                                                                                                                                                                                                                           | List of plugins to load              |
| account_aliases    | dict   | {}                                                                                                                                                                                                                                                                           | Aliases for accounts in gnucash file |
