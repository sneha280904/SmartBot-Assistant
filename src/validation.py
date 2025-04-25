# <---------- IMPORTS ---------->
import re
import phonenumbers
import dns.resolver
from disposable_email_domains import blocklist


# <---------- VALIDATION CLASS ---------->
class validation:

    # <---------- Phone Number Validation ---------->

    @staticmethod
    def is_possible_number(number, region='IN'):
        """
        Check if a phone number is possible and valid using phonenumbers library.
        Default region is India ('IN').
        """
        try:
            parsed = phonenumbers.parse(number, region)
            return phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed)
        except:
            return False

    @staticmethod
    def validatePhoneNumber(phone): 
        """
        Validate Indian phone number using regex and phonenumbers.
        Must start with 6-9 and be 10 digits long.
        """
        phoneRegex = r'^[6-9]\d{9}$'  # Valid for Indian mobile numbers only
        if re.match(phoneRegex, phone) and validation.is_possible_number(phone, region='IN'):
            return True
        return False

    # <---------- Email Validation ---------->

    @staticmethod
    def is_disposable(email):
        """
        Check if the email domain is in the disposable email blocklist.
        """
        domain = email.split('@')[-1]
        return domain.lower() in blocklist

    @staticmethod
    def has_mx_record(email):
        """
        Check if the email domain has an MX record (used for sending emails).
        """
        domain = email.split('@')[-1]
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return len(records) > 0
        except Exception:
            return False

    @staticmethod
    def validateEmail(email):
        """
        Validate email using regex, check for disposable domains and verify MX records.
        """
        emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(emailRegex, email) and not validation.is_disposable(email) and validation.has_mx_record(email):
            return True
        return False
