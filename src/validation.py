# # Validate 

# import re

# class validation:
#     def validatePhoneNumber(phone):
#         phoneRegex = r'^(?:\+91|)[1-9][0-9]{9}$'
#         if re.match(phoneRegex, phone):
#             return True
#         return False

#     def validateEmail(email):
#         emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#         if re.match(emailRegex, email):
#             return True
#         return False
    

# Validate 
import re
import phonenumbers
import dns.resolver
from disposable_email_domains import blocklist

class validation:

    @staticmethod
    def is_possible_number(number, region='IN'):
        try:
            parsed = phonenumbers.parse(number, region)
            return phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed)
        except:
            return False

    @staticmethod
    def validatePhoneNumber(phone): 
        phoneRegex = r'^[6-9]\d{9}$'  # Valid for Indian mobile numbers only
        if re.match(phoneRegex, phone) and validation.is_possible_number(phone, region='IN'):
            return True
        return False

    @staticmethod
    def is_disposable(email):
        domain = email.split('@')[-1]
        return domain.lower() in blocklist

    @staticmethod
    def has_mx_record(email):
        domain = email.split('@')[-1]
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return len(records) > 0
        except Exception:
            return False

    @staticmethod
    def validateEmail(email):
        emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(emailRegex, email) and not validation.is_disposable(email) and validation.has_mx_record(email):
            return True
        return False

    # def is_valid_email(email):
    # if not validateEmail(email):
    #     return False
    # if is_disposable(email):
    #     return False
    # domain = email.split('@')[-1]
    # if not has_mx_record(domain):
    #     return False
    # return True







## Final Code 

# import re
# import requests

# class validation:
#     NUMVERIFY_API_KEY = "01cef913a1b6bf4d507bd021e7e035c8"
#     MAILBOXLAYER_API_KEY = "234d8c2810063a56fc405d4d2640ae81"

#     @staticmethod
#     def validatePhoneNumber(phone):
#         # General international format check (E.164)
#         phoneRegex = r'^\+?[1-9][0-9]{7,14}$'
#         if not re.match(phoneRegex, phone):
#             return False

#         # API check to verify real number
#         url = f"http://apilayer.net/api/validate?access_key={validation.NUMVERIFY_API_KEY}&number={phone}&format=1"
#         try:
#             response = requests.get(url)
#             data = response.json()
#             return data.get("valid", False) and data.get("line_type") == "mobile"
#         except Exception as e:
#             print(f"Phone validation error: {e}")
#             return False

#     @staticmethod
#     def validateEmail(email):
#         # Basic format check
#         emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#         if not re.match(emailRegex, email):
#             return False

#         # API check to verify real email
#         url = f"http://apilayer.net/api/check?access_key={validation.MAILBOXLAYER_API_KEY}&email={email}&smtp=1&format=1"
#         try:
#             response = requests.get(url)
#             data = response.json()
#             return data.get("smtp_check", False)
#         except Exception as e:
#             print(f"Email validation error: {e}")
#             return False
