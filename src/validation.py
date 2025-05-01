# <---------- for validate  ---------->
# Import necessary modules
import re  # Regular expressions for pattern matching
import phonenumbers  # Library to parse, format, and validate phone numbers
import dns.resolver  # DNS resolver to check for MX (Mail Exchange) records
from disposable_email_domains import blocklist  # List of disposable email domains

# Define the validation class containing static methods for validation
class validation:

    # Method to check if a phone number is possible and valid for the given region
    @staticmethod
    def is_possible_number(number, region='IN'):
        try:
            # Parse the phone number according to the specified region (default is India)
            parsed = phonenumbers.parse(number, region)
            # Check if the number is possible and valid
            return phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed)
        except:
            # Return False if there is an error parsing or validating the number
            return False

    # Method to validate an Indian phone number using a regular expression and phonenumbers library
    @staticmethod
    def validatePhoneNumber(phone): 
        # Regular expression to match Indian mobile numbers (starting with 6-9 followed by 9 digits)
        phoneRegex = r'^[6-9]\d{9}$'  # Valid for Indian mobile numbers only
        # Check if the phone number matches the regex pattern and is a possible and valid number
        if re.match(phoneRegex, phone) and validation.is_possible_number(phone, region='IN'):
            return True  # Return True if valid
        return False  # Return False if invalid

    # Method to check if an email is from a disposable email provider
    @staticmethod
    def is_disposable(email):
        # Split the email address by '@' and check if the domain is in the blocklist (disposable providers)
        domain = email.split('@')[-1]
        return domain.lower() in blocklist  # Return True if domain is disposable, otherwise False

    # Method to check if the email domain has a valid MX (Mail Exchange) record
    @staticmethod
    def has_mx_record(email):
        # Extract the domain part of the email
        domain = email.split('@')[-1]
        try:
            # Try to resolve the domain's MX record (indicating it can receive emails)
            records = dns.resolver.resolve(domain, 'MX')
            return len(records) > 0  # Return True if there are MX records, otherwise False
        except Exception:
            # Return False if there is an error resolving MX records (e.g., domain doesn't exist)
            return False

    # Method to validate an email address using a regex and additional checks for disposable domain and MX records
    @staticmethod
    def validateEmail(email):
        # Regular expression to validate general email structure
        emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        # Check if the email matches the regex, is not disposable, and has valid MX records
        if re.match(emailRegex, email) and not validation.is_disposable(email) and validation.has_mx_record(email):
            return True  # Return True if valid
        return False  # Return False if invalid




# # <---------- for no condition validation ---------->

# # Import necessary module for regular expression handling
# import re

# # Define the validation class containing methods for phone number and email validation
# class validation:

#     # Method to validate a phone number (Indian format) with optional country code (+91)
#     def validatePhoneNumber(phone):
#         # Regular expression to match Indian phone numbers with an optional +91 country code
#         phoneRegex = r'^(?:\+91|)[1-9][0-9]{9}$'  # Match numbers starting with 1-9 followed by 9 digits, with optional +91
#         # Use re.match to check if the phone number matches the regex pattern
#         if re.match(phoneRegex, phone):
#             return True  # Return True if valid phone number
#         return False  # Return False if invalid phone number

#     # Method to validate an email address based on general email format
#     def validateEmail(email):
#         # Regular expression to match general email structure
#         emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Match emails with letters, digits, and allowed symbols
#         # Use re.match to check if the email matches the regex pattern
#         if re.match(emailRegex, email):
#             return True  # Return True if valid email format
#         return False  # Return False if invalid email format

