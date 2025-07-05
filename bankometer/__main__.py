
from bankometer import Methods
from orgasm import command_executor_main, get_classes
from orgasm.http_rest import serve_rest_api
import os 

def main():
    if "BANKOMETER_REST_API" in os.environ:
        serve_rest_api([Methods], 8000, "0.0.0.0")
        return
    command_executor_main(Methods, explicit_params=True)

if __name__ == "__main__":
    main()