import os
import logging
from dotenv import load_dotenv
import boto3
from typing import Tuple, List
import config as c

load_dotenv('.env')

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = c.AWS_REGION

IMPORT_BUCKET = c.IMPORT_BUCKET
DATA_DIR = c.DATA_DIR
LOG_DIR = c.LOG_DIR
PUBMED_FILE = c.PUBMED_FILE

SCRIPT_NAME = (os.path.basename(__file__)).split(".")[0]
LOGGING_LEVEL = logging.DEBUG

# Conceal function
def conceal(string: str) -> str:
    string = list(string)
    for index in range(3, len(string) - 3):
        string[index] = "*"
    return "".join(string)

# Request credentials function
def request_credentials(default_access_key: str,
                        default_secret_key: str,
                        logger: logging.Logger) -> Tuple[str, str]:
    logger.info("Parsing AWS credentials...")

    try:
        access_key = default_access_key
        secret_key = default_secret_key
        logger.info("Successfully retrieved AWS credentials.")
        logger.debug("Access key: %s", conceal(access_key))
        logger.debug("Secret key: %s", conceal(secret_key))

    except Exception as e:
        logger.error("Failed to retrieve AWS credentials!")
        logger.error(f"{e}")
        access_key, secret_key = None, None

    return access_key, secret_key

# Get client function
def get_client(access_key: str,
               secret_key: str,
               region: str,
               logger: logging.Logger) -> boto3.client:
    logger.info("Fetching boto3 client...")

    try:
        client = boto3.client('s3',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name=region
                              )
        logger.info("Retrieved client successfully.")
        logger.debug(f"Client: {client}")

    except Exception as e:
        logger.error("Failed to get client!")
        logger.error(f"{e}")

    return client

def list_xml_files(client: boto3.client, bucket: str, logger: logging.Logger) -> List[str]:
    """Get xml files from an s3 bucket, returns them as a list."""
    logger.info("Listing XML files in the bucket...")

    try:
        response = client.list_objects_v2(Bucket=bucket)
        xml_files = [content['Key'] for content in response.get('Contents', []) if content['Key'].endswith('.xml')]
        xml_files = [file for file in xml_files if "joshua" in file]

        logger.info(f"Found {len(xml_files)} XML files.")
        logger.debug(f"XML files: {xml_files}")


    except Exception as e:
        logger.error("Failed to list XML files!")
        logger.error(f"{e}")
        xml_files = []

    return xml_files

# Write XML content to a file
def write_xml_to_file(xml_content: str, file_path: str, logger: logging.Logger) -> None:
    logger.info(f"Writing XML content to file: {file_path}")

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(xml_content)
        logger.info(f"Successfully wrote to {file_path}")

    except Exception as e:
        logger.error(f"Failed to write XML content to {file_path}!")
        logger.error(f"{e}")

def download_and_merge_xml_files(client: boto3.client, bucket: str, xml_files: List[str], merged_file_path: str, logger: logging.Logger) -> None:
    """Compiles all the XML fiels to a sinbgle file, however has to
    do some stitching to stop duplication of elements that must appear
    only once"""
    logger.info("Downloading and merging XML files..")

    merged_content = "<PubmedArticleSet>\n"
    doctype_declaration = None

    for xml_file in xml_files:
        logger.debug(f"Downloading and merging: {xml_file}..")
        try:
            response = client.get_object(Bucket=bucket, Key=xml_file)
            content = response['Body'].read().decode('utf-8')

            if not doctype_declaration:
                doctype_pos = content.find('<!DOCTYPE')
                if doctype_pos != -1:
                    doctype_end_pos = content.find('>', doctype_pos) + 1
                    doctype_declaration = content[doctype_pos:doctype_end_pos]
                    content = content[:doctype_pos] + content[doctype_end_pos:].strip()

            content = content.replace('<?xml version="1.0"?>', '').strip()
            content = content.replace('<PubmedArticleSet>', '').replace('</PubmedArticleSet>', '').strip()

            merged_content += content + "\n"
            logger.info(f"Downloaded: {xml_file}")

        except Exception as e:
            logger.error(f"Failed to download {xml_file}!")
            logger.error(f"{e}")

    merged_content += "</PubmedArticleSet>"

    if doctype_declaration:
        merged_content = doctype_declaration + "\n" + merged_content

    write_xml_to_file(merged_content, merged_file_path, logger)

def main():
    # Setup logging and performance tracking
    performance_logger = c.setup_subtle_logging(f"{LOG_DIR}/{SCRIPT_NAME}_performance")
    profiler = c.start_monitor()
    logger = c.setup_logging(f"{LOG_DIR}/{SCRIPT_NAME}", LOGGING_LEVEL)
    logger.info("---> Logging initiated.")

    # Request AWS credentials
    logger.info("---> Getting AWS credentials..")
    access_key, secret_key = request_credentials(AWS_ACCESS_KEY, AWS_SECRET_KEY, logger)

    # Get the S3 client
    logger.info("---> Setting up s3 client..")
    client = get_client(access_key, secret_key, AWS_REGION, logger)

    # List XML files
    logger.info("---> Identifying XML files..")    
    xml_files = list_xml_files(client, IMPORT_BUCKET, logger)

    # Download and merge XML files
    logger.info("---> Downloading and merging XML files..")
    merged_file_path = f'{DATA_DIR}/{PUBMED_FILE}'
    download_and_merge_xml_files(client, IMPORT_BUCKET, xml_files, merged_file_path, logger)

    logger.info("---> Terminating performance tracking and saving data..")
    c.stop_monitor(SCRIPT_NAME, profiler, performance_logger)

if __name__ == "__main__":
    main()