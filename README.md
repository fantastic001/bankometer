

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
# Working with bank statements 

bankometer can convert your PDF bank statements to CSV format. To do that, you can execute:

    python -m bankometer process_statement -b <bank> -p <path_to_pdf> 

Supported banks are:

- Yettel 

Output CSV file will be created in the CWD. 

Also, we can sum up all transactions with same description and category:

    python -m bankometer dedup_statement -p <path_to_csv> -c <categories>

This deduplicates transactions from a bank statement csv file using the categories spec.

Transaction belongs to category if it contains category name in
description. If transaction belongs to multiple categories, it is assigned to the first one.

If transaction does not belong to any category, it will be printed as is, without category.

Categories sum expenses and incomes.

Categories are separated by pipe symbol `|`. For instance, if you want to sum up all transactions with "food" and "transport" in description, you can execute:

    python -m bankometer dedup_statement -p <path_to_csv> -c "food|transport"