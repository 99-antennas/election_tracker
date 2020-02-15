#!/usr/bin/env python
# coding: utf-8

"""
Generic data cleaning utilities
"""

import os
import datetime as dt
from glob import glob
import numpy as np
import pandas as pd
from collections import OrderedDict
from urllib.parse import urlparse
import requests
import mimetypes
import json

#jupyter
import IPython

from ast import literal_eval
import urllib
import re
# import phonenumbers
# from email_validator import validate_email, EmailNotValidError

from src.settings import PROJECT, PREPEND_OBJ, OUTPUT_PATH, SLUG, TODAY

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

##### FILE OUTPUT UTILITIES ####
class Prepender(object):
    """
    Writes a prepend object to the first few lines of an output file
    Used to add meta data (project, date, company and source attribution) to outputed csvs for the purpose of version control.
    To import csv use skip rows to avoid importing meta data.

    sample code:
    with Prepender('test_d.out') as f:
    # Must write individual lines in reverse order
    f.write_line('This will be line 3')
    f.write_line('This will be line 2')
    f.write_line('This will be line 1')

    with Prepender('test_d.out') as f:
    # Or, use write_lines instead - that maintains order.
    f.write_lines(
        ['This will be line 1',
         'This will be line 2',
         'This will be line 3',
        ]
    )
    """
    def __init__(self,
                 file_path,
                ):
        # Read in the existing file, so we can write it back later
        with open(file_path, mode='r') as f:
            self.__write_queue = f.readlines()

        self.__open_file = open(file_path, mode='w')

    def write_line(self, line):
        self.__write_queue.insert(0,
                                  "%s\n" % line,
                                 )

    def write_lines(self, lines):
        lines.reverse()
        for line in lines:
            self.write_line(line)

    def close(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.__write_queue:
            self.__open_file.writelines(self.__write_queue)
        self.__open_file.close()

def prepend_details(filepath, src_lines=None):
    lines = []
    if src_lines:
        lines.append(src_lines)
    lines.append('')
    with Prepender(filepath) as f:
        f.write_lines(lines)

def create_filepath(name, ext, date=False, path=OUTPUT_PATH, slug=SLUG):
    """
    creates a filepath from vars
    """
    if date:
        date = "_" + TODAY
    else:
        date = ''
        
    if slug:
        slug = slug + "_"
    else:
        slug = ''
        
    filename = slug + name + date + ext
    filepath = os.path.join(path, filename)
    print(filepath)
    return filepath

def output_to_csv(df, filename, ext='.csv', path=OUTPUT_PATH, include_index=False, index_name=None, date=None, source_credit=None, slug=None):
    """
    include index?
    sets index name for index column (optional, default = 'index')
    creates filepath (default ext. = .txt if ext=None)
    sets encoding to 'utf-8'
    outputs file to csv
    prepends source credit to file
    Default: prepend_obj
    Optional: source credit
    """
    if index_name:
        df.index.name = index_name
    else:
        df.index.name = "index"
    if not ext:
        ext = '.txt'
    if not source_credit:
        source_credit = None
    if not path:
        path = os.getcwd()
    if not slug:
        slug = None
    try:
        filepath = create_filepath(filename, ext, date=date, path=path, slug=slug)
        #save to csv
        df.to_csv(filepath, encoding='utf-8', index=include_index)
        #add sourcing
        prepend_details(filepath, src_lines=source_credit)
    except Exception as e:
        print("Error: {}".format(e))

def output_to_json(data, filename, ext=None, date=None, path=OUTPUT_PATH, slug=SLUG):
    if not ext:
        ext = '.txt'
    if not path:
        path = os.getcwd()
    if not slug:
        slug = None
    try:
        filepath = create_filepath(filename, ext, date=date, path=path, slug=slug)
        #save to json
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print("Error: {}".format(e))

#####  DATA CLEANING UTILITIES ####
def search_values(myDict, searchFor):
    """
    searches for string in values of a dictionary
    non-recursive
    """
    value = None
    for k in myDict:
        for v in myDict[k]:
            if searchFor in v:
                value = k
    return value

def test_for_array(col):
    result = [True if (isinstance(x, list)) else False for x in col]
    if False in result:
        return False


def as_percent(var1, var2):
    as_percent = round((var1/var2)*100, 2)
    as_percent = "{0:.2f}%".format(as_percent)
    return as_percent

def hasNumbers(inputString):
    """
    identifies if a digit is in a string, returns digit
    used to extract digits from character strings
    """
    return any(char.isdigit() for char in inputString)

def getNumber(string):
    """
    extracts all digits as a complete number from an input string
    """
    numbers = []
    if hasNumbers(string):
        for char in string:
            if char.isdigit():
                numbers.append(char)
    number = ''.join(numbers)
    return number

def isNotEmptyString(s):
    """
    check if a string value is empty("" or "  ")
    """
    if isinstance(s, str):
        return bool(s and s.strip())
    else:
        pass

def test_for_empty_strings(df):
    """
    Tests dataframe for empty strings
    Returns a set of empty string values for each column of the df
    Used to search and replace empty strings
    """
    results = {}
    for col in df:
        result = [x for x in df[col] if isNotEmptyString(x) == False]
        if result:
            print('{}: Fail'.format(col))
            results[col] = list(set(result))
    return results

def convert_np_type(obj):
    """Takes an object of type np (np.float, np.int, etc.) converts to python standard type"""
    if isinstance(obj, np.generic):
        return np.asscalar(obj)
    else:
        return obj

def convert_to_int(obj):
    """takes a single value of numpy.float64 or numpy.int64 and converts to standard python int"""
    if isinstance(obj, (np.float64, np.int64)):
        return int(obj)
    else:
        return obj

#convert float (really mixed integer) dtypes to object for all cols in a df
def identify_mixed_int(df):
    """
    Function for identifying columns that include int and NaN's.
    Pandas converts columns with null values and integers to 'float64'
    This can cause numerous issues.
    See: https://stackoverflow.com/questions/11548005/numpy-or-pandas-keeping-array-type-as-integer-while-having-a-nan-value?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    This function is used in conjunction with convert_mixed_int to resolve this issue.
    Used to test for 'float64' cols in df that should be kept as float
    """
    mixed_int_cols = []
    for col in df.columns:
        if str(df[col].dtype) == 'float64':
            mixed_int_cols.append(col)
    return mixed_int_cols

def convert_mixed_int(df, cols_to_convert=None):
    """
    Converts mixed integer and NaN's col in a Pandas DataFrame from 'float64' to 'object' cols
    See: identify_mixed_int for info
    Takes a Pandas Series
    returns

    """
    print("Converted columns:")
    if not cols_to_convert:
        cols_to_convert = identify_mixed_int(df)
    try:
        for col in cols_to_convert:
            if str(df[col].dtype) == 'float64':
                df[col] = df[col].dropna().apply(lambda x: str(int(x)))
                print(col)
            else:
                print('{} Failed: Attempted to convert a col that was not of type float'.format(col))
    except Exception as e:
        print(e)
    return df

def convert_mixed_int_cols(df, int_cols): 
    """
    Takes a dataframe and list of columns that should be of type 'int'
    Used to deal with mixed integer columns that have been converted by pandas to float due to missing values 
    Checks if the column can be converted to integer; if not... 
    Uses custom function to convert individual values in column from float to int
    Returns the dataframe with 
    - integer columns with no missing values converted to int
    - integer columns with missing values converted from dtype 'float' to 'object'
    (which can include a mix of integers and np.nan values.) 
    """
    for col in int_cols: 
        try: 
            #try to convert to int
            df[col] = df[col].astype(int)
            return df
        except Exception as e: 
            print(e)
            df[col] = df[col].astype(float, errors='ignore')
            df = convert_mixed_int(df, cols_to_convert=[col])
            return df

def make_ordinal(n):
    ordinal = "%d%s"%(n, {1:"st", 2:"nd", 3:"rd"}.get(n if n < 20 else n%10, "th"))
    return ordinal

def rreplace(s, old, new, occurrence):
    """
        Reverse string replace. Finds items starting at end of string.
        Replaces first occurance
        Returns a string with the value replaced by a new value
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)

def check_complete_cols(df, complete_cols):
    """
    Used for testing null values in a list of columns in a dataframe.
    Takes a Pandas dataframe and a list of columns to test for null values.
    If column has null values appends col name to list.
    Returns list of columns that have null values.
    """
    print('Failed:')
    hasNull = []
    for col in complete_cols:
        if df[col].isnull().values.any():
            print(col)
            hasNull.append(col)
    return hasNull

def strlist_to_list(col):
    """
    Converts a string-dtype list to list dtype
    Used to convert lists inside dataframes back into lists,
    typically on loading csv's
    """
    col = [literal_eval(x) for x in col]
    return col

def search_list(search_term, first_list):
    """
    Searches a list for the index of an item containing search term
    Returns the item index
    """
    try:
        find = [first_list.index(x) for x in first_list if search_term in x]
        for x in find:
            print("List item: " + first_list[find])
        return find
    except IndexError:
        print('List item not found')

def search_df_col(search_str, df, col_name):
    """
    Searches a column of a database for a string value
    Returns the index where value is True
    """
    index = df[df[col_name].str.contains(search_str)].index.tolist()
    return index

def search_replace(search_term, first_list, second_list):
    """
    Searches a list for the index of an item containing search term
    Searches a second list for the index of an item containing a search term
    Replaces the value of the item in second list with value of the
    search result in the first list.
    Returns the second list
    """
    find = [first_list.index(x) for x in   first_list if search_term in x][0]
    value = first_list[find]
    print("First list: " + value)
    find_src = [second_list.index(x) for x in second_list if search_term in x][0]
    print("Second list: " + second_list[find_src])
    #replace
    second_list[find_src] = value
    print("Second list updated: " + second_list[find_src])
    return second_list

def search_replace_value(search_term, first_list, value):
    """
    Searches a list for the index of an item containing search term
    Replaces the value of the item in list with new value
    Returns the list
    """
    find = [first_list.index(x) for x in first_list if search_term in x]
    for item in find:
        print("List item: " + first_list[item])
    #replace
    new_list = [x.replace(x, value) if search_term in x else x for x in first_list]
    replaced = [new_list.index(x) for x in new_list if search_term in x]
    for item in replaced:
        print("List item updated: " + new_list[item])
    return new_list

def search_replace_by_index(search_str, new_value, df, col_name,
                            replace_col=None, index_list=None):
    """
    Searches a df by index for a search string
    replaces the value in the matching column with new value
    regex (r'^some_string$') to find exact match
    """
    if not index_list:
        index_list = search_df_col(search_str, df, col_name)
    if not replace_col:
        replace_col = col_name
    if len(index_list) != 0:
        print("Index list: {}".format(index_list))
        for i in index_list:
            current_value = df.loc[i, col_name]
            #new_value = current_value.replace(search_str, new_value)
            df.loc[i, replace_col] = new_value.strip()
            print("Current value: {} \n Updated value {}".format(current_value, new_value))
    else:
        print("Index list empty or search string not found.")
    return index_list

def cross_table_lookup(lookup_val, lookup_table, search_col, return_col):
    """ looks up a value in a lookup table
        takes a search value, a dataframe, dataframe column to search,
        and dataframe column from which to return value
        searches for an exact match of a specific value in a specific column of a table
        returns the value of another column in the same table
        returns list of matches
     """
    try:
        result = lookup_table.loc[lookup_table[search_col] == lookup_val, return_col].tolist()
        return result
    except IndexError as e:
        result = np.nan
        if not lookup_val:
            print("Value not found: {}".format(lookup_val))
        return result

def test_for_multiple(lookup_val, lookup_table, search_col, return_col):
    """ looks up a value in a lookup table
        takes a search value, a dataframe, dataframe column to search,
        and dataframe column from which to return value
        searches for an exact match of a specific value in a specific column of a table
        if more than one record returns True
        if no result returns np.nan
        used with cross table lookup to identify searches that will return more than one result
    """
    try:
        result = lookup_table.loc[lookup_table[search_col] == lookup_val, return_col]
        if len(result) > 1:
            return True
        else:
            return False
    except IndexError as e:
        result = np.nan
        if not pd.isnull(lookup_val):
            print("Value not found: {}".format(lookup_val))
        return result

def map_new_df_cols(df, field_map):
    """
    Takes a source dataframe and a dict mapping the source dataframe fields to a new df
    with fields named differently.

    For each row in the df,
    Maps the data in each column to the new column names
    Creates a new row.
    Appends the new row to a new dataframe.
    Returns the new dataframe.
    """
    new_data = []
    for i in df.index:
        new_row = OrderedDict({})
        for k, v in field_map.items():
            if v in df.columns:
                new_row[k] = df.loc[i, v]
            else:
                new_row[k] = v
        new_data.append(new_row)
    new_df = pd.DataFrame(new_data)
    return new_df

##### CENSUS DATA UTILITIES ####
def replace_by_state(st_df, df, state_abbr):
    print(len(df))
    df = df.loc[df['state'] != state_abbr, :]
    print(len(df))
    df = pd.concat([st_df, df], ignore_index=True)
    print(len(df))
    return df

def check_cnty_by_state(us_cnty, county_c):
    """
    For each record in the source dataset (us_cnty, Census data)
    checks that for each county in the source data
    there is a matching record with the same
    county name by state (using stripped county names) in
    the validation set (county_c)
    returns any county, state combinations that are not an exact
    match in the validation set
    Used for checking that all Census data counties are included in the dataset
    """
    no_match = []
    for i in us_cnty.index:
        cnty = us_cnty.loc[i]['cnty_name']
        st = us_cnty.loc[i]['UPS_CODE']
        find_rows = county_c.loc[
            (county_c['county_name'] == cnty) &\
            (county_c['state'] == st)]
        if find_rows.empty == True:
            no_match.append((cnty, st))
        else:
            pass
    return no_match

def check_by_cnty_fips(us_cnty, county_c):
    """
    For each record in the dataset (county_c)
    checks that [all] county name, state and fips code
    have a matching recording in src dataset (census) (using stripped county names)
    returns any records that are not an exact match
    """
    no_match = []
    for i in county_c.index:
        cnty = county_c.loc[i]['county_name']
        st = county_c.loc[i]['state']
        fips = county_c.loc[i]['fips_code']
        find_rows = us_cnty.loc[
            (us_cnty['cnty_name'] == cnty) &\
            (us_cnty['UPS_CODE'] == st) &\
            (us_cnty['FIPS_CODE'] == fips)
        ]
        if len(find_rows) > 0:
            pass
        else:
            no_match.append((i, cnty, st, fips))
    return no_match

 ##### REVIEW MANUAL UPDATES UTILITIES ####
def compare_by_col(df, compare_cols, print_result=True):
    not_same = []
    for col in compare_cols:
        vals = df[col].tolist()
        #print(vals)
        #compare_vals = ['' if x is np.nan else x for x in vals] #strip np.nan's for comparison
        #print(vals)
        #check if all equivalent null
        #not_null_set = set(compare_vals) - set([np.nan, '', None, ""])
        col_set = set(vals)
        len_set = len(col_set)

        #only one value in column, i.e. all rows in column contain same value
        if len_set == 1:
            pass
        elif col_set == set(['', np.float('nan')]):
            print("here's a set comparison case {}".format(vals))
        elif vals == ['', np.nan]:
            pass
        elif vals == [np.nan, '']:
            pass
        else:
            col_set = list(col_set) # create list
            col_set = col_set[::-1] #reverse_list to print in order of appearance

            if print_result:
                print("{}: {}: ".format(col, list(col_set)))
            else:
                pass

            not_same.append([col, list(col_set)])
    return not_same

def review_changes(src_df, val_df, compare_cols, filename, validated_by_col='validated',
                   display_note='validation_notes'):
    """
    Used for reviewing manually validated/updated tables against the source table.
    Compares one table (src) with a second manually validated table (val)
    Allows user to accept or reject changes by row, by cell.

    Takes:
        src_df:  the original dataset
        val_df:  the data set with changes
        compare_cols: a list of columns to compare (assumes both tables have the same col names)
        filename: to save changes to as json (allows progress to be saved if work interrupted)
        validat_by_col: to track who reviewed (2nd validator) the data (optional)
        display_note: field to add notes as you go (optional)

    Looks up the 'id' col in the src df in the val df
    If matches, compares matching row, col by col, identfying diffs
    Allows user to accept the change for each cell
    Stores user input in a json dictionary
    If error, returns json
    else continues to next id match until complete.

    Once the review is complete use 'apply changes' to update the validated dataset (val_df)
    with only those changes that have been accepted by the reviewer (2nd validator)

    """
    endProgram = 0
    val_len = len(val_df)
    num = 0
    accepted_changes = []
    no_changes = []
    val_cols = src_df.columns.tolist() #compare only columns in both datasets.

    while (endProgram != 1) & (num <= val_len):
        print("Record {} of {}".format(num, val_len))
        try:
            validator = val_df.iloc[num][validated_by_col]
            idval = val_df.iloc[num]['id']
            find_rows = src_df.loc[src_df['id'] == idval, :]
            val_row = val_df.iloc[num][val_cols]
            test = find_rows.append(val_row)

            col_diff = compare_by_col(test, compare_cols, print_result=True)

            if not col_diff:
                #accepted = 'no_change'
                no_changes.append({'position': num, 'id': idval})
                num += 1

            else:
                #show results
                IPython.display.display(test)
                print(val_row[display_note])

                outcome = {} #row outcome
                issues_note = None
                for col in col_diff:

                    #get current col values
                    current_col = compare_by_col(test, [col[0]], print_result=False)

                    #Prompt for a new transaction
                    userInput = input("{} Accept changes? 'Yes, no or pass? ".format(col[0]))
                    userInput = userInput.lower()

                    #Validate input
                    while userInput not in {'yes', 'no', 'y', 'n', 'pass', 'end'}:
                        print("Invalid input. Please try again.")
                        userInput = input("Accept changes? Yes, no, or pass? ('end' to escape.) n/{}".format(col[1]))
                        userInput = userInput.lower()

                    if userInput == 'end':
                        print("Ending program at: index {}".format(num))
                        data = [accepted_changes, no_changes]
                        output_to_json(data, filename, ext='.json',
                                       path="../data/99antennas/")
                        yield (accepted_changes, no_changes)
                        #accepted_changes.append('skipped')
                        endProgram = 1

                    #if userInput == 'rewind':
                    #    print("Going to: index {}".format(num))
                    #    yield (accepted_changes, no_changes)
                    #    num -= 1
                    #    endProgram = 1

                    else:
                        if (userInput == 'yes') or (userInput == 'y'):
                            accepted = val_row[col[0]]
                        elif (userInput == 'no') or (userInput == 'n'):
                            accepted = 'no change'
                        elif userInput == 'pass':
                            accepted = 'pass'
                            issues_note = input("Issues?: ")
                    outcome[col[0]] = accepted #add column outcome to row outcome

                result = {}
                result['result'] = outcome #row outcome
                result['position'] = num #index position
                result['id'] = idval #match value
                if validator:
                    result['validated_by'] = validator #validated by
                if issues_note:
                    result['issues'] = issues_note #any issues with validation process
                else:
                    result['issues'] = None

                accepted_changes.append(result)

                data = [accepted_changes, no_changes]
                output_to_json(data, filename, ext='.json', path="../data/99antennas/")

                yield (accepted_changes, no_changes)
                num += 1

        except Exception as e:
            print(e)
            print("Ending program at: index {}".format(num))
            data = [accepted_changes, no_changes]
            output_to_json(data, filename, ext='.json',
            path="../data/99antennas/")
            yield (accepted_changes, no_changes)
            endProgram = 1


def apply_changes(responses, src_df, new_col="accept_changes_notes"):
    change_idx = []
    change_list = []
    failed = []

    if new_col: #add col for validation notes
        src_df[new_col] = np.nan

    for response in responses:
        try:
            result = response['result']
            matchId = response['id']
            idx = src_df.loc[src_df['id'] == matchId, :].index.tolist()
            for n in idx:
                changes = {}

                #add validation notes
                if response['issues']:
                    src_df.loc[n, new_col] = response['issues']
                    changes[new_col] = response['issues']

                #update values for each result item (col, value)
                updated = {}
                for k, v in result.items():
                    if (v != 'no change') and (v != 'pass'):
                        col = k
                        src_df.loc[n, col] = v
                        #track changes
                        updated[k] = v

                    if updated:
                        changes['updated'] = updated

                #track changes
                if changes:
                    changes['pos'] = n
                    changes['id'] = matchId
                    change_list.append(changes)
                    change_idx.append(n)

        except Exception as e:
            failed.append([e, response])
            print(e, response)
            pass
    return (change_idx, change_list, failed)


##### VALIDATE COMMON DATA TYPES UTILITIES ####
def validate_url(url):
    """
    validates url scheme (i.e. absolute path)
    """
    min_attr = ('scheme', 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True
        else:
            return False
    except:
        return False

def valid_url(url):
    '''
    validates the url by checking the url schema
    **OR**
    testing for a response code 200, 403 (Forbidden)
    intended to allow for non valid schemas that result in valid response codes
    '''
    if validate_url(url) == True and test_url_path(url) in [200, 403]:
        valid_url = True
    else:
        valid_url = False
    return valid_url

def validate_phone_numbers(series, region):

    """
    Validates phone numbers in a data series
    Takes a pandas series and a region (i.e. 'US')
    Replaces invalid numbers with 'None'
    prints length of values parsed (for exception test checking against length of series)
    prints lenth of failed values
    Returns a list of validated numbers, and a list of failed values by positional index
    """
    parsed_values = []
    failed = {}
    for pos, num in enumerate(series):
        if not pd.isnull(num):
            try:
                parsed = phonenumbers.parse(num, region)
                if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
                    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                    parsed_values.append(formatted)
                else:
                    failed[pos] = num
                    num = None
                    parsed_values.append(num)
            except Exception as e:
                failed[pos] = num
                print(pos, num, e)
                num = None
                parsed_values.append(num)
        else:
            num = None
            parsed_values.append(num)

    print("{} Length series".format(len(series)))
    print("{} Length values parsed".format(len(parsed_values)))
    print("{} Length values failed".format(len(failed)))
    return parsed_values, failed

def validate_emails(series):
    parsed_values = []
    failed = {}
    for pos, email in enumerate(series):
        if not pd.isnull(email):
            email = email.strip()
            try:
                valid = validate_email(email) # validate and get info
                formatted = valid["email"] # replace with normalized form
                parsed_values.append(formatted)
            except EmailNotValidError as e:
                #email is not valid, exception message is human-readable
                print(pos, email, str(e))
                failed[pos] = email
                email = None
                parsed_values.append(email)
        else:
            email = None
            parsed_values.append(email)

    print("{} Length series".format(len(series)))
    print("{} Length values parsed".format(len(parsed_values)))
    print("{} Length values failed".format(len(failed)))
    return parsed_values, failed

def validate_urls(series):
    parsed_values = []
    failed = {}
    for pos, url in enumerate(series):
        if not pd.isnull(url):
            url = url.strip()
            try:
                valid = valid_url(url) # validate, returns True, False
                if valid:
                    parsed_values.append(url)
                else:
                    failed[pos] = url
                    url = None
                    parsed_values.append(url)
            except Exception as e:
                print(pos, url, e)
                failed[pos] = url
                url = None
                parsed_values.append(url)
        else:
            url = None
            parsed_values.append(url)

    print("{} Length series".format(len(series)))
    print("{} Length values parsed".format(len(parsed_values)))
    print("{} Length values failed".format(len(failed)))
    return parsed_values, failed

def valid_year(year):
    """
    Takes a year in the form of a string or an integer
    Returns True if between 1900 and 2100
    """
    if isinstance(year, int):
        year = str(year)
    if year and year.isdigit():
        if int(year) >= 1900 and int(year) <= 2100:
            return True
        else:
            return False

def validate_years(series):
    parsed_values = []
    failed = {}
    for pos, year in enumerate(series):
        if not pd.isnull(year):
            try:
                valid = valid_year(year) # validate, returns True, False
                if valid:
                    parsed_values.append(year)
                else:
                    failed[pos] = year
                    year = None
                    parsed_values.append(year)
            except Exception as e:
                print(pos, year, e)
                failed[pos] = year
                year = None
                parsed_values.append(year)
        else:
            parsed_values.append(year)

    print("{} Length series".format(len(series)))
    print("{} Length values parsed".format(len(parsed_values)))
    print("{} Length values failed".format(len(failed)))

    return parsed_values, failed

def valid_image(url):
    """
    Takes a url to an image
    Returns True if mimetype is a valid image mimetype
    """
    try:
        valid_img_types = ['.gif', '.jpe', '.jpg', '.png', '.webp']
        mimetype = get_mimetype(url)
        if mimetype in valid_img_types:
            return True
        else:
            return False
    except:
        return False

def validate_images(series):
    parsed_values = []
    failed = {}
    for pos, value in enumerate(series):
        if not pd.isnull(value):
            try:
                valid = valid_image(value) # validate, returns True, False
                if valid:
                    parsed_values.append(value)
                else:
                    failed[pos] = value
                    value = None
                    parsed_values.append(value)
            except Exception as e:
                print(pos, value, e)
                failed[pos] = value
                value = None
                parsed_values.append(value)
        else:
            parsed_values.append(value)

    print("{} Length series".format(len(series)))
    print("{} Length values parsed".format(len(parsed_values)))
    print("{} Length values failed".format(len(failed)))

    return parsed_values, failed

def split_name(series, remove_suffix=True): 
    """
    Takes a dataframe column or Series of full names 
    Splits the text string into an array 
    Returns a list of arrays
    Optional, remove suffix 
    Used for extracting first and last names from complex full name fields
    """
    name_split = series.str.lower().str.split(' ')
    names = []
    suffixes = ['jr.', 'sr.', 'jr', 'sr', ', jr.', ', sr.', 'ii', 'iii', 'iv', 'v']
    for name in name_split: 
        if remove_suffix == True:
            name = [name.remove(x) if x in suffixes else x for x in name]
            name = [x for x in name if x is not None]
        names.append(name)
    return names

def extract_middle_initial(series):
    """
    Used to extract the middle initial from the first name field
    Takes a Pandas series.
    Identifies by index which values contain a middle initial using regex.
    If found, stores the middle initial value in a dict along with the index
        rsrips the value from the original string
        stores the updated string along with the index in a dict
    Returns both the extracted and updated dicts

    """

    extracted = {}
    updated = {}
    for i in series.index.tolist():
        string = series[i]
        middle_regex = r'\s[A-Z][.]$'
        result = re.findall(middle_regex, string)
        if result:
            result = result[0].strip()
            print(result)
            extracted[i] = result
            replace_value = r'{}$'.format(result)
            string = string.rstrip(replace_value).strip()
            updated[i] = string
        else:
            pass
    return extracted, updated

