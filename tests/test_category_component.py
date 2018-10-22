# Create a file called test_category_component.py in tests and does the following things:
# 1. Mocks the Blockchain Client's functionality of taking in a data provider and outputting an ED Directory. 
# 	 My recommended solution is to create a function that returns hardcoded output for a specific input,
# 	 and then return this function as a part of a @pytest.fixture called blockchain_client (so that all 
#    tests have clean and easy access).
# 2. Mocks the DB Client's functionality of taking in a category and returning a list of data providers. 
#    My recommended solution is the same as above.
# 3. Tests whether a category successfully retrieves a list of ED Directories with the right data providers.
# 4. Tests whether a category with no associated data providers throws an exception right away.
# If you feel there are edge cases that I haven't mentioned, feel free to add those as well.
import pytest

