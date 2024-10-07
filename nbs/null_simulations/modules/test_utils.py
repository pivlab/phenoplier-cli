import re
from utils import trim_spaces, remove_newline

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

# To run the tests, use: pytest -v test_string_cleaning.py