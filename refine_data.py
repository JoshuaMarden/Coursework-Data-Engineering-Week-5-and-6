"""Refines the data by extracting more information from the strings in the data parquet"""

import os
import logging
import spacy
import pandas as pd
import config as c
from rapidfuzz import fuzz, process
import pycountry

DATA_DIR =  c.DATA_DIR
LOG_DIR = c.LOG_DIR
CLEANED_DATA = c.EXTRACTED_DATA
REFINED_DATA = c.REFINED_DATA
ADDRESSES = c.ADDRESSES
ALIASES = c.ALIASES
FUZZY_THRESHOLD_LENIENT = c.FUZZY_THRESHOLD_LENIENT
SPACEY_DATASET = c.SPACEY_DATASET
LOW_MEMORY = c.LOW_MEMORY

SCRIPT_NAME = (os.path.basename(__file__)).split(".")[0]
LOGGING_LEVEL = logging.DEBUG


def import_csv(file_path: str, memory_capacity: bool, logger: logging.Logger) -> pd.DataFrame:
    """imports a csv to a pandas dataframe"""
    logger.info("Reading CSV file to datafrmae..")
    try:
        df = pd.read_csv(file_path, low_memory=memory_capacity)
        logger.info("CSV converted to datframe")
        return df
    except Exception as e:
        logger.error("Error reading CSV")
        logger.error(e)

def extract_countries_set(addresses_df: pd.DataFrame, logger: logging.Logger) -> set:
    """Extracts countries to a tuple"""
    logger.info("Building countries set..")

    try:
        countries = set(addresses_df['country'])
        logger.info("Countries extracted.")
        return countries
    except Exception as e:
        logger.debug("Error extracting countries.")
        logger.debug(e)

def extract_insitiutions_set(aliases_df: pd.DataFrame, logger: logging.Logger) -> set:
    """Extracts insititution names to a tuple"""
    logger.info("Building institutions set..")
    try:
        institutions = set(aliases_df['alias'])
        logger.info("Institutions extracted.")
        return institutions
    except Exception as e:
        logger.debug("Error extracting institutions.")
        logger.debug(e)


def fuzzy_match(comparison_strings: set | str, ideal_strings: list | tuple, threshold: int, logger: logging.Logger) -> str:
    """Tries to find the best match between possible location or list of possible locations,
    and a list of GRID location names, returns best match. Checks for pefect matches
    first for effiency
    e.g. [Shoreditch, London, Englnd] and [France, England, Germany] -> England
          will return 'England'."""

    logger.debug(f"Using fuzzy search to find best match with {comparison_strings}..")

    if not isinstance(comparison_strings, set):
        comparison_strings = set([comparison_strings])

    for comparison_string in comparison_strings:
        for ideal in ideal_strings:
            if ideal in comparison_string:
                logger.debug(f"Perfect match found: {ideal}")
                return ideal
    
    best_str = ""
    best_score = -1
    for comparison_string in comparison_strings:
        match = process.extractOne(comparison_string, ideal_strings, scorer=fuzz.token_sort_ratio)
        if match and match[1] > best_score and match[1] > threshold:
            best_score = match[1]
            best_str = match[0]

    if best_str != "":
        logger.debug(f"Best accepted match: {best_str}.")
        logger.debug(f"Match score: {best_score}.")
        return best_str
    else:
        logger.debug("No good match found.")
        return "Unknown"

def is_subdivision(name: str) -> bool:
    """
    Checks if a given name matches a subdivision in any country.
    Stops a state like Maryland MD, being matched to Maldova, MD.
    i.e. stops red-herrings.
    """
    try:
        pycountry.subdivisions.lookup(name)
        return True
    except LookupError:
        return False

def pycountry_match(comparison_strings: set | str, logger: logging.Logger):
    """
    Check elements of a set against the alpha-2, alpha-3, official name,
    and common name of all countries. If any are a 1:1 match,
    return the official name.
    """
    logger.debug("Searching for matches with pycountry dataset:")
    logger.debug(comparison_strings)

    if not isinstance(comparison_strings, set):
        comparison_strings = set([comparison_strings])

    for string in comparison_strings:

        if string == 'UK': # The UK is special and is handled here.
            string = 'GB'

        if is_subdivision(string):
            continue

        logger.debug(f"Searching for match against: {string}")
        for country in pycountry.countries:
            if (string.lower() in {country.alpha_2.lower(), country.alpha_3.lower(), country.name.lower()} or
                string.lower() in {country.official_name.lower()} if hasattr(country, 'official_name') else False):
                logger.debug(f"Match found with: {country.name}")
                return country.name
    return None

def spacey_match(comparison_strings: set | str, nlp: any, label: str, logger: logging.Logger) -> set:
    """Takes a string and (using spacey) identifies words in that
    string tha are associated with the label provided. 
    Also handles a set of strings.
    e.g. 'the rain in Spain' returns 'Spain' with label 'GPE' """

    logger.debug("Searching for Spacey associations with:")
    logger.debug(comparison_strings)

    if not isinstance(comparison_strings, set):
        comparison_strings = set([comparison_strings])

    possible_matches = set()

    for string in comparison_strings:
        logger.debug(f"Searching for associations with: {string}, using label: {label}")
        doc = nlp(string)
        logger.debug("NLP document:")
        logger.debug(doc)

        if not doc:
            logger.debug("Spacey matching could not idenfiy any meaninful attributes.")
            return possible_matches

        for ent in doc.ents:
            if ent.label_ == label:
                possible_matches.add(ent.text)

    logger.debug(f"Possible matches: {possible_matches}")
    return possible_matches

def identify_matching_country(affiliation: str, countries: tuple, threshold: int, nlp: any, logger: logging.Logger):
    """Uses spacey to extract possible countries from a string, tries to match
    those to a list of countries. Also tries simple fuzzy matching if spacey finds nothing."""
    logger.debug(f"Attempting to extract country from {affiliation}..")

    possible_countries = spacey_match(affiliation, nlp, "GPE", logger)

    logger.debug("Trying to match spacey output to country..")

    if not possible_countries:
        logger.debug("Country could not be derived from the affiliation data.")
        return 'Unknown'

    match = pycountry_match(possible_countries, logger)
    if match:
        logger.debug("Matched Spacey output to PyCountry dataset.")
        return match

    match = fuzzy_match(possible_countries, countries, threshold, logger)
    if match:
        logger.debug("Fuzzy matched spacey output to list of GRID countries.")
        return match

    logger.warning(f"Continuing with '{match}' as best match.")
    return match


def identify_matching_institution(affiliation: str, institutions: set[str], threshold: int, nlp: any, logger: logging.Logger) -> str:
    """Uses spacey to extract possible institutions from a string, tries to match
    those to a list of insitutions. Also tries simple fuzzy matching if spacey finds nothing."""
    logger.debug(f"Attempting to extract institution from {affiliation}..")

    possible_institutions = spacey_match(affiliation, nlp, "ORG", logger)    

    logger.debug("Trying to match spacey output to institution..")

    if not possible_institutions:
        logger.debug("Country could not be derived from the affiliation data.")
        return 'Unknown'
    
    match = fuzzy_match(possible_institutions, institutions, threshold, logger)
    if match:
        logger.debug("Fuzzy matched spacey output to list of institutions.")
        return match

    match = fuzzy_match(affiliation, institutions, threshold, logger)
    if match:
        logger.debug("Matched using simple fuzzy search.")
        return match
    
    logger.warning(f"Continuing with '{match}' as best match.")
    return match


def add_countries(dataframe: pd.DataFrame, countries: tuple, threshold: int, nlp: any, logger: logging.Logger) -> pd.DataFrame:
    """Adds a 'country' column to the DataFrame; extracts the country
    from the affiliations column"""
    logger.debug("Adding countries..")
    matched_countries = ()
    for affiliation in dataframe['affiliation']:
        logger.debug(f"Extracting country from: {affiliation}")
        country = identify_matching_country(affiliation, countries, threshold, nlp, logger)
        logger.debug(f"Country identified as: {country}")
        matched_countries += (country,)
    dataframe['country'] = matched_countries
    return dataframe

def add_institutions(dataframe: pd.DataFrame, institutions: tuple, threshold: int, nlp: any, logger: logging.Logger) -> pd.DataFrame:
    """Adds an 'institution' column to the DataFrame; extracts the institution
    from the affiliations column"""
    logger.debug("Adding institutions..")
    matched_institutions = ()
    for affiliation in dataframe['affiliation']:
        logger.debug(f"Extracting institution from: {affiliation}")
        institution = identify_matching_institution(affiliation, institutions, threshold, nlp, logger)
        logger.debug(f"Institution identified as: {institution}")
        matched_institutions += (institution,)
    dataframe['institution'] = matched_institutions
    return dataframe

def check_report_missing_data(df, logger: logging.Logger):
    """Checks how much data is missing from the dataframe and logs it."""
    logger.info("Checking to see how much data is missing from columns..")

    for col in df.columns:

        df[col] = df[col].astype(str)

        count_empty = (df[col] == "").sum()
        count_nan = df[col].isna().sum()
        count_unknown = (df[col] == "Unknown").sum()

        missing_count = count_empty + count_nan + count_unknown
        missing_percent = (missing_count / len(df)) * 100

        logger.info(f"{col} missing {missing_count} / {len(df)} ({missing_percent:.2f}%)")



def main():

    # Setup logging and perforance tracking
    performance_logger = c.setup_subtle_logging(f"{LOG_DIR}/{SCRIPT_NAME}_performance")
    profiler = c.start_monitor()
    logger = c.setup_logging(f"{LOG_DIR}/{SCRIPT_NAME}", LOGGING_LEVEL)
    logger.info("---> Logging initiated..")

    # Get data from parquet
    logger.info("---> Reading file from parquet..")
    df = pd.read_parquet(f'{DATA_DIR}/{CLEANED_DATA}')

    # Setup natural language processor
    logger.info("---> Setting up Spacey NLP..")
    nlp = spacy.load(SPACEY_DATASET)

    # Get list of countries and instituons from CSV files
    logger.info("---> Getting GRID countries and institutions data from CSV..")
    addresses_df = import_csv(f"{DATA_DIR}/{ADDRESSES}", LOW_MEMORY, logger)
    institutions_df = import_csv(f"{DATA_DIR}/{ALIASES}", LOW_MEMORY, logger)
    logger.info("---> Converting GRID countries and institutions data to tuples..")
    countries = extract_countries_set(addresses_df, logger)
    institutions = extract_insitiutions_set(institutions_df, logger)

    # Add countries and institutions to dataframe
    logger.info("---> Adding countries to the dataframe..")
    df = add_countries(df, countries, FUZZY_THRESHOLD_LENIENT, nlp, logger)
    logger.info("---> Adding institutions to the dataframe..")
    df = add_institutions(df, institutions, FUZZY_THRESHOLD_LENIENT, nlp, logger)

    logger.info("---> Checking data quality..")
    check_report_missing_data(df, logger)

    logger.info("---> Saving dataframe as parquet..")
    df.to_parquet(f'{DATA_DIR}/{REFINED_DATA}', engine='pyarrow')

    # Stop tracking performance and save data
    logger.info("---> Terminating performance tracking and saving data..")
    c.stop_monitor(SCRIPT_NAME, profiler, performance_logger)


    
    logging.info("---> Done.")

if __name__ == "__main__":

    main()