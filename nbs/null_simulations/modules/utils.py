import re

def trim_spaces(command):
    # Replace multiple spaces with a single space
    trimmed_command = re.sub(r'\s+', ' ', command).strip()
    return trimmed_command


def remove_newline(command):
    # Remove newline characters
    return command.replace('\n', '')


def test_trim_spaces():
    # Test case 1: Multiple spaces between words
    assert trim_spaces("hello   world") == "hello world"
    
    # Test case 2: Leading and trailing spaces
    assert trim_spaces("  hello world  ") == "hello world"
    
    # Test case 3: Tabs and multiple spaces
    assert trim_spaces("hello\t\tworld   test") == "hello world test"
    
    # Test case 4: Only spaces
    assert trim_spaces("     ") == ""
    
    # Test case 5: No spaces
    assert trim_spaces("helloworld") == "helloworld"

def test_remove_newline():
    # Test case 1: String with newlines
    assert remove_newline("hello\nworld") == "helloworld"
    
    # Test case 2: String with multiple newlines
    assert remove_newline("hello\n\nworld\n") == "helloworld"
    
    # Test case 3: String without newlines
    assert remove_newline("hello world") == "hello world"
    
    # Test case 4: Empty string
    assert remove_newline("") == ""
    
    # Test case 5: String with only newlines
    assert remove_newline("\n\n\n") == ""