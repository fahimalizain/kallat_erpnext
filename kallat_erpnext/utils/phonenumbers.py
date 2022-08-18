from contextlib import suppress
import phonenumbers

DEFAULT_REGION = "IN"
DEFAULT_FORMAT = phonenumbers.PhoneNumberFormat.E164


def format_number(number: str):
    """
    Format the Contact numbers in a specific format
    """
    parsed_number = parse_number(number)
    if not phonenumbers.is_valid_number(parsed_number):
        raise phonenumbers.NumberParseException(1, "Is not a valid number")

    return phonenumbers.format_number(parsed_number, DEFAULT_FORMAT)


def parse_number(number: str):
    """
    Tries to parse the incoming number
    Re-tries to parse in IN Region if fails
    """
    with suppress(phonenumbers.NumberParseException):
        return phonenumbers.parse(number)

    return phonenumbers.parse(number, DEFAULT_REGION)
