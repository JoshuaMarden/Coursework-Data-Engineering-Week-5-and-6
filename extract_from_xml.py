import os
import xml.etree.ElementTree as ET
import pandas as pd
import config as c
import cProfile
import pstats
from datetime import datetime
import logging
import re

DATA_DIR =  c.DATA_DIR
LOG_DIR = c.LOG_DIR
PUBMED_FILE = c.PUBMED_FILE
CLEANED_DATA = c.REFINED_DATA
SCRIPT_NAME = os.path.basename(__file__)


def open_file(file_path: str, logger: logging.Logger) -> str:
    """Opens a file, returns it as a string"""
    logger.info(f"Opening file {file_path}..")
    try:
        with open (file_path, "r",encoding="UTF-8") as file:
            logger.info(f"Opened {file_path}.")
            return file.read()
    except Exception as e:
        logger.error(f"Failed to open file {file_path}.")
        logger.error(e)
        return None
    
def convert_string_to_element_tree(xml_str: str, logger: logging.Logger) -> ET:
    """Converts xml string an element tree"""
    logger.info("converting XML to element tree..")
    try:
        element_tree = ET.fromstring(xml_str)
        logger.info("element tree created succesfully.")
        return element_tree
    except Exception as e:
        logger.error("Could not create element tree.")
        logger.error(e)
        return None

def build_date(day: str, month: str, year: str, logger: logging.Logger) -> datetime:
    """take strings and build a dattime object with them"""
    logger.debug("Building date..")
    try:
        pub_date = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
        formatted_date = pub_date.strftime("%d-%m-%Y")
        logger.debug(f"Date created succesfully {str(formatted_date)}")
        return formatted_date
    except Exception as e:
        logger.error("Could not build date.")
        logger.error(e)
        return datetime.strptime("01-01-1970")

def get_mesh_descriptors(article: ET, logger: logging.Logger) -> list[str]:
    """gets the mesh desriptors for an article"""
    logger.debug("Getting mesh descriptors..")
    mesh_descriptors = []
    try:
        for mesh_heading in article.findall(".//MeshHeading"):
            descriptor = mesh_heading.find("DescriptorName")
            if descriptor is not None:
                ui = descriptor.attrib.get('UI')
                if ui and ui.startswith('D'):
                    mesh_descriptors.append(ui)
        logger.debug("Retrieved mesh descriptors succesfully:")
        logger.debug(mesh_descriptors)
        return mesh_descriptors
    
    except Exception as e:
        logger.error("Could not retrieve mesh descriptors")
        logger.error(e)
        return mesh_descriptors

def get_key_words(article: ET, logger: logging.Logger) -> list[str]:
    """gets key words """
    logger.debug("Getting key words..")
    try:
        keywords = [kw.text for kw in article.findall(".//Keyword")]
        logging.debug("Retrieved key words succesfully:")
        logging.debug(keywords)
        return keywords
    except Exception as e:
        logger.error("Could not retrieve key words")
        logger.error(e)
        return []

def get_medline_info(article: ET, logger: logging.Logger) -> dict:
    """Gets the medline info from an article"""
    logger.debug("Getting medline info..")
    medline = {}
    try:
        medline_info = article.find(".//MedlineJournalInfo")
        if medline_info is not None:
            medline['country'] = medline_info.findtext(".//Country")
            medline['medline_ta'] = medline_info.findtext(".//MedlineTA")
            medline['nlm_unique_id'] = medline_info.findtext(".//NlmUniqueID")
            medline['issn_linking'] = medline_info.findtext(".//ISSNLinking")
        else:
            medline = {'country': None, 'medline_ta': None, "nlm_unique_id": None, "issn_linking": None}

        logger.debug("Retrieved medline info succesfully:")
        logger.debug(medline)
        return medline

    except Exception as e:
        logger.error("Could not retrieve medline info.")
        logger.error(e)
        return medline

def get_authors_and_affiliations(article: ET, logger: logging.Logger) -> tuple:
    logger.debug("Getting authors and affiliations..")
    authors = []
    try:
        for auth in article.findall(".//Author"):
            last_name = auth.findtext("./LastName")
            first_name = auth.findtext("./ForeName")
            affiliations = [aff.text for aff in auth.findall(".//Affiliation")]
            authors.append({
                "first_name": first_name,
                "last_name": last_name,
                "affiliations": affiliations,
            })
        logger.debug("Retrieved authors and affiliations:")
        logger.debug(authors)
        return authors
    except Exception as e:
        logger.error("Could not retireve authors and affiliations")
        logger.error(e)
        return authors

def get_abstract(article: ET, logger: logging.Logger) -> str:
    """Get the abstract for an article"""
    logger.info("Getting abstract..")
    try:
        abstract_text = " ".join([abstract.text or "" for abstract in article.findall(".//AbstractText")]).strip()
        logger.debug("Retrieved abstract succesfully:")
        logger.debug(abstract_text)
        return abstract_text
    except Exception as e:
        logger.error("Could not retrieve abstract.")
        logger.error(e)
        return ''
    
def extract_postcode(text: str, logger: logging.Logger) -> str | None:
    """Extract postcode from affiliations if exists"""
    logger.debug("Checking for postcode..")
    uk_pattern = re.compile(r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b')
    us_pattern = re.compile(r'\b\d{5}(?:-\d{4})?\b')
    canadian_pattern = re.compile(r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b')

    patterns = [uk_pattern, us_pattern, canadian_pattern]

    postcode = None
    for pattern in patterns:
        postcode = pattern.findall(text)
        if postcode != None:
            logger.debug(f"Postcode found: {postcode}")
            break
    logger.debug(f"No postcode detected.")
    return postcode

def extract_initials(text: str, logger: logging.Logger) -> str:
    """Gets intials from a name"""
    logger.debug(f"Getting author initials for {text}..")
    search_pattern = re.compile(r'\b\w*([A-Z])\w*\b')
    initials = "".join(search_pattern.findall(text))
    logger.debug(f"Author intials: {initials}")
    return initials


def extract_postcode(text: str, logger: logging.Logger) -> str | None:
    """Extract postcode from affiliations if exists"""
    logger.debug("Checking for postcode..")
    uk_pattern = re.compile(r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b')
    us_pattern = re.compile(r'\b\d{5}(?:-\d{4})?\b')
    canadian_pattern = re.compile(r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b')

    patterns = [uk_pattern, us_pattern, canadian_pattern]

    postcode = []
    for pattern in patterns:
        postcode = pattern.findall(text)
        if postcode != []:
            logger.debug(f"Postcode found: {postcode}")
            return ", ".join(postcode)
            break
    logger.debug(f"No postcode detected.")
    return None

def extract_email(text: str, logger: logging.Logger) -> str | None:

    logger.debug("Checking for email..")
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email = email_pattern.findall(text)
    if email != []:
        logger.debug(f"email found: {email}")
        return ", ".join(email)
    else:
        logger.debug("no email identified")
        return None


def segregate_by_affiliation(authors_and_affiliations: dict, logger: logging.Logger) -> dict:
    """takes a dict of forename, lastname, and affiliatons,
    makes a copy of each name per affiliation, returns as dict,
    also extracts email, postcode, and author intials."""

    logger.debug("Creating unique author : affiliation pairs..")
    author_affiliation_pairs = []
    logger.debug(authors_and_affiliations)
    try:
        for entry in authors_and_affiliations:
            pair = {}
            logger.debug(entry['first_name'])
            
            if entry['affiliations'] == []:
                logging.debug("Affiliations not given.")
                entry['affiliations'] = 'None Given'
            if entry['first_name'] in [None, "None"]:
                logging.debug("First name not given.")
                entry['first_name'] = ''
            if entry['last_name'] in [None, "None"]:
                logging.debug("Last name not given.")
                entry['last_name'] = ''
            
            if isinstance(entry['affiliations'], list):
                for affiliation in entry['affiliations']:
                    pair["name"] = " ".join([entry["first_name"], entry["last_name"]])
                    pair["initials"] = extract_initials(pair["name"], logger)
                    pair['affiliation'] = affiliation
                    pair['email'] = extract_email(affiliation, logger)
                    pair['postcode'] = extract_postcode(affiliation, logger)
                    author_affiliation_pairs.append(pair)
            else:
                pair["name"] = " ".join([entry["first_name"], entry["last_name"]])
                pair['affiliation'] = entry['affiliations']

        logger.debug("Created one author-affiliation entry for each affiliation..")
        logger.debug(author_affiliation_pairs)
        return author_affiliation_pairs
    except Exception as e:
        logger.error("Could not create unique pairs")
        logger.error(e)


def article_to_dataframe(root: ET, logger: logging.Logger) -> pd.DataFrame:
    """Extracts and prints the required information from the XML."""
    logger.info("Extracting data from XML article..")

    unique_attributes = {}
    complete_data_sets = []

    for article in root.findall("PubmedArticle"):
        logger.info("\n\n------------------------------------------------")
        logger.info("Extracting simple data..")

        try:
            title = article.findtext(".//ArticleTitle")
            logger.info(f"Article title: {title}")
        except Exception as e:
            logger.error("Could not retrieved title.")
            logger.error(e)

        unique_attributes['journal'] = article.findtext(".//Journal/Title")
        unique_attributes['iso_abbreviation'] = article.findtext(".//Journal/ISOAbbreviation")
        unique_attributes['year'] = article.findtext(".//PubDate/Year")
        unique_attributes['pmid'] = article.findtext(".//PMID")
        unique_attributes['doi'] = article.findtext(".//ELocationID[@EIdType='doi']")
        unique_attributes['abstract'] = get_abstract(article, logger)
        unique_attributes['key_words'] = get_key_words(article, logger)
        unique_attributes['mesh_descriptors'] = get_mesh_descriptors(article, logger)
        
        logger.info("Trying to extract authors and their affiliations..")
        authors_and_affiliations = get_authors_and_affiliations(article, logger)
        
        logger.info("Trying to extract medline information..")
        medline_info = get_medline_info(article, logger)
        unique_attributes = unique_attributes | medline_info

        logger.info("Trying to extract publication dates..")
        pub_day = article.findtext(".//PubDate/Day")
        pub_month = article.findtext(".//PubDate/Month")
        pub_year = article.findtext(".//PubDate/Year")
        if pub_day and pub_month and pub_year:
            try:
                logger.info("Day, month, year, extracted.")
                logger.info("Attempting to build a date..")
                unique_attributes['formatted_date'] = build_date(pub_day, pub_month, pub_year, logger)
            except Exception as e:
                unique_attributes['formatted_date'] = None
                logger.error("Could not build date.")
                logger.error(e)
            
        logger.info("Making unique author affiliations unique..")
        author_affilation_pairs = segregate_by_affiliation(authors_and_affiliations, logger)
        
        for pair in author_affilation_pairs:
            unified_set = pair | unique_attributes
            complete_data_sets.append(unified_set)

    for i in complete_data_sets:
        print("----------")
        print(i)

    df = pd.DataFrame(complete_data_sets)
    logger.info("10 Examples of entries:")
    logger.info(df.head(10))
    return df


def main(file_path):

    performance_logger = c.setup_subtle_logging(f"{LOG_DIR}/{SCRIPT_NAME}_performance")
    profiler = c.start_monitor()
    logger = c.setup_logging(f"{LOG_DIR}/{SCRIPT_NAME}")

    xml_content = open_file(file_path, logger)
    root = convert_string_to_element_tree(xml_content, logger)
    df = article_to_dataframe(root, logger)
    
    df.to_parquet(f'{DATA_DIR}/{CLEANED_DATA}.parquet', engine='pyarrow')

    c.stop_monitor(SCRIPT_NAME, profiler, performance_logger)


if __name__ == "__main__":
    
    file_path = f"{DATA_DIR}/{PUBMED_FILE}"
    main(file_path)
    
