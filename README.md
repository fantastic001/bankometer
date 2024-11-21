

# Introduction 

Bankometer is a tool for managing your bank accounts 

# Usage 


### 1. Configuration File Example (`bankometer_config.yaml`)

```yaml
accounts:
    bank_a:
    username: "user_a"
    password: "pass_a"
    module: "bank_modules.bank_a"

    bank_b:
    username: "user_b"
    password: "pass_b"
  module: "bank_modules.bank_b"
```

- **`username` and `password`**: Login credentials for the bank.
- **`module`**: The Python module implementing specific behavior for the bank. These modules contain the `login` and `get_transactions` functions.

---

### **2. Environment Variable**

Set the location of the configuration file:

```bash
export BANKOMETER_CONFIG=/path/to/custom_config.yaml
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
bankometer bank_a --list-transactions
```
Logs into `bank_a` and lists all transactions retrieved from the bank module.

---

#### **Filter Transactions by Minimum Amount**
```bash
bankometer bank_a --list-transactions --min-amount 100
```
Fetches transactions for `bank_a` and only displays those with an amount greater than or equal to 100.

---

#### **Filter Transactions by Maximum Amount**
```bash
bankometer bank_a --list-transactions --max-amount 50
```
Fetches transactions for `bank_a` and only displays those with an amount less than or equal to 50.

---

#### **Filter Transactions by Keyword**
```bash
bankometer bank_a --list-transactions --keyword "Grocery"
```
Fetches transactions for `bank_a` and displays only those containing the word "Grocery" in their description.

---

#### **Combine Filters**
```bash
bankometer bank_a --list-transactions --min-amount 50 --max-amount 200 --keyword "Store"
```
Fetches transactions for `bank_a` and applies multiple filters: amounts between 50 and 200, and descriptions containing the word "Store."

---

### **4. Adding Support for a New Bank**

1. **Create a New Bank Module**

   Create a Python file (e.g., `bank_modules/bank_c.py`) with the following structure:

   ```python
   # bank_modules/bank_c.py

   def login(username, password):
       print(f"Logging into Bank C as {username}...")
       # Add login logic here

   def get_transactions():
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
     module: "bank_modules.bank_c"
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
bankometer bank_a --list-transactions
``` 

This setup allows you to dynamically support multiple banks by defining their behavior in separate modules and referencing them in the configuration file.