"""Config files"""
import os
import logging
import cProfile
import pstats
from io import StringIO

# dir where data is stored
DATA_DIR = "data"
# dir where logs are stored
LOG_DIR = "logs"

# Raw pubmed data files in xml format
PUBMED_FILE = "pubmed_result_sjogren.xml"
# Extracted PubMed Files
EXTRACTED_DATA = "extracted_data.parquet"
# Data that has been refined, with more attributes extracted
REFINED_DATA = "refined_data.parquet"
# GRID data
ADDRESSES = "addresses.csv"
ALIASES = "aliases.csv"
INSTITUTES = "institutes.csv"

# Threshold for fuzzy searches to accept a string as a match
FUZZY_THRESHOLD_STRICT = 92
FUZZY_THRESHOLD_LENIENT = 80

# Dataset to use with spacey
SPACEY_DATASET = "en_core_web_lg"

# Set to false if system does not have limited memdory for faster
# CSV to pandas conversion
LOW_MEMORY = False

# Functions

def setup_logging(log_name: str, logging_level=logging.DEBUG):
    """setup logging"""
    logger = logging.getLogger(log_name)
    logger.setLevel(logging_level)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f'{log_name}.log')
    error_file_handler = logging.FileHandler(f'{log_name}_errors.log')

    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    error_file_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_file_handler)

    return logger

def setup_subtle_logging(log_name, logging_level=logging.DEBUG):
    """setup logging"""
    logger = logging.getLogger(log_name)
    logger.setLevel(logging_level)

    file_handler = logging.FileHandler(f'{log_name}.log')

    file_handler.setLevel(logging.DEBUG)
    logger.propagate = False


    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger

def start_monitor() -> cProfile.Profile:

    profiler = cProfile.Profile()
    profiler.enable()

    return profiler

def stop_monitor(script_name: str, profiler: cProfile.Profile, logger) -> None:

    profiler.disable()

    script_name = script_name.split('.')[0]
    binary_profile = f"{LOG_DIR}/{script_name}.prof"

    profiler.dump_stats(binary_profile)

    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats()
 
    logger.info(s.getvalue())