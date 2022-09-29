from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class CustomPasswordValidator:

    def __init__(self, min_length=1):
        self.min_length = min_length

    def validate(self, password, user=None):
        #regex to check for special characters
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        
        #checks for number
        if not any(char.isdigit() for char in password):
            raise ValidationError(_('Password must contain at least %(min_length)d digit.') % {'min_length': self.min_length})
        
        #checks for any letters
        if not any(char.isalpha() for char in password):
            raise ValidationError(_('Password must contain at least %(min_length)d letter.') % {'min_length': self.min_length})

        #checks for upper case
        if not any(char.isupper() for char in password):
            raise ValidationError(_('Password must contain at least %(min_length)d uppercase letter.') % {'min_length': self.min_length})
        
        #checks for any special characters
        if not any(char in special_characters for char in password):
            raise ValidationError(_('Password must contain at least %(min_length)d special character.') % {'min_length': self.min_length})
    
    #message to display to user creating account
    def get_help_text(self):
        return "Password requires a number, an uppercase letter and a special character"
