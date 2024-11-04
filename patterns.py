count_patterns = [
    r'count of invoices generated in (\w+ \d{4}|\d{1,2}-\d{4})',
    r'invoice count for (\w+ \d{4}|\d{1,2}-\d{4})',
    r'how many invoices in (\w+ \d{4}|\d{1,2}-\d{4})',
]

# List of regex patterns for listing invoices
list_patterns = [
    r'show me the list of invoices (present|generated) in (\w+ \d{4}|\d{1,2}-\d{4})',
    r'list me the invoices in (\w+ \d{4}|\d{1,2}-\d{4})',
    r'can you please show me the invoices in (\w+ \d{4}|\d{1,2}-\d{4})',
    r'i need to check all the invoices in (\w+ \d{4}|\d{1,2}-\d{4})',
]

pdf_request_patterns = [
    r'give me the pdf for ([A-Z0-9\-]+)',
    r'can you please find me the pdf for ([A-Z0-9\-]+)',
    r'fetch me the pdf for ([A-Z0-9\-]+)',
    r'please get the pdf for ([A-Z0-9\-]+)',
]

greetings = ["hello", "hi", "hey", "greetings"]

farewell = ["bye", "goodbye", "see you"]