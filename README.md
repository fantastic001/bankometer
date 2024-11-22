

# Introduction 

Bankometer is a tool for managing your bank accounts 

# Usage 


### 1. Configuration File Example (`bankometer_config.yml`)

```yaml
accounts:
    bank_a:
    username: "user_a"
    password: "pass_a"
    module: "bank_a.BankA"

    bank_b:
    username: "user_b"
    password: "pass_b"
  module: "bank_b.BankB"
```

- **`username` and `password`**: Login credentials for the bank. Some banks will require manual login. Options available are plugin-specific.
- **`module`**: The Python module implementing specific behavior for the bank. These modules contain the `login` and `get_transactions` functions.

---

### **2. Environment Variable**

Set the location of the configuration file:

```bash
export BANKOMETER_CONFIG=/path/to/custom_config.yml
```

If the environment variable is not set, the default config file is `~/.config/bankometer_config.yaml` in the current working directory.

---

### **3. Commands and Usage Examples**

#### **Login to a Bank**
```bash
bankometer bank_a
```
This command logs into `bank_a` using the credentials and module defined in the configuration file. If the login fails, the program exits with an error message.

---

#### **List All Transactions**
```bash
bankometer bank_a list_transactions start_date end_date
```
Logs into `bank_a` and lists all transactions retrieved from the bank module from the specified start date and end date. Dates are specified in format `YYYY-MM-DD`.

---


---

### **4. Adding Support for a New Bank**

1. **Create a New Bank Module**

   Create a Python file (e.g., `bank_modules/bank_c.py`) with the following structure:

   ```python
   # bank_modules/bank_c.py
   from bankometer import BankInterface
   import pandas as pd
  class BankC(BankInterface)
    def login(self):
        print(f"Logging into Bank C as {username}...")
        # Add login logic here

    def get_transactions(self, start_date, end_date) -> pd.DataFrame:
        # Return a list of transactions (simulate for now)
        return [
            {"date": "2024-11-01", "amount": -30, "description": "Subscription Fee"},
            {"date": "2024-11-02", "amount": 1000, "description": "Freelance Payment"},
        ]
   ```

2. **Update the Configuration File**

   Add a new entry for the bank:

   ```yaml
   bank_c:
     username: "user_c"
     password: "pass_c"
     module: "bank_c.BankC"
   ```

3. **Use Bankometer**

   ```bash
   bankometer bank_c --list-transactions
   ```

---

### **5. Workflow with Custom Config File**

Set the custom config file path using an environment variable:

```bash
export BANKOMETER_CONFIG=/custom/path/to/config.yaml
bankometer bank_a list_transactions 2024-10-15 2024-10-20
``` 

This setup allows you to dynamically support multiple banks by defining their behavior in separate modules and referencing them in the configuration file.