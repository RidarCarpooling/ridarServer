import importlib.util
import os

# Create module specification
def gen_check_mac_value(params):
    spec = importlib.util.spec_from_file_location(
        "ecpay_payment_sdk",
        "ecpay_payment_sdk.py"
    )

    # Create module from specification
    module = importlib.util.module_from_spec(spec)

    # Load the module
    spec.loader.exec_module(module)

    # Create an instance of the ECPayPaymentSdk class
    ecpay_sdk = module.ECPayPaymentSdk(MerchantID=os.environ.get("MERCHANT_ID"), HashKey=os.environ.get("HASH_KEY"), HashIV=os.environ.get("HASH_IV"))

    # Call the generate_check_value method
    check_mac_value = ecpay_sdk.generate_check_value(params)
    # Now you have the check MAC value
    return check_mac_value
