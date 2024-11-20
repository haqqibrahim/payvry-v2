def format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format for Nigeria
    Example: 08033456778 -> 2348033456778
    """
    # Remove any spaces, dashes, or plus signs
    clean_number = ''.join(filter(str.isdigit, phone))
    
    # If number starts with 0, replace with 234
    if clean_number.startswith('0'):
        clean_number = '234' + clean_number[1:]
    # If number doesn't start with 234, add it
    elif not clean_number.startswith('234'):
        clean_number = '234' + clean_number
        
    return clean_number
