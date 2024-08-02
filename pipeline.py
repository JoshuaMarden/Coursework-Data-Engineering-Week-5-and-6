"""Runs entire pipeline from beginning to end"""

"""
This includes importing the raw data, saving it, cleaning it,
refining it, and pushing it to an S3 bucket.
"""
import logging
from dotenv import load_dotenv
import os
import import_data
import extract_from_xml as extract
import refine_data as refine
import export_data 
from send_email import setup_client, notify 
import config as c

LOG_DIR = c.LOG_DIR

SCRIPT_NAME = (os.path.basename(__file__)).split(".")[0]
LOGGING_LEVEL = logging.DEBUG

load_dotenv('.env')


def main():

    email_ses = setup_client()
    notify(email_ses, True)

    print("___.----══════=====^^*^^====══════----.___")
    print("||            Starting Pipeline          ||")
    print("==========================================")

    logger = c.setup_logging(f"{LOG_DIR}/{SCRIPT_NAME}", LOGGING_LEVEL)

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||            Logging Initiated          ||")
    logger.info("==========================================")
    logger.info("")

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||             Importing Data            ||")
    logger.info("==========================================")
    import_data.main()

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||            Extracting Data            ||")
    logger.info("==========================================")
    extract.main()

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||             Refining Data             ||")
    logger.info("==========================================")
    refine.main()

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||            Exporting Data             ||")
    logger.info("==========================================")
    export_data.main()

    logger.info("___.----══════=====^^*^^====══════----.___")
    logger.info("||           PIPELINE COMPLETE!          ||")
    logger.info("==========================================")
    notify(email_ses, False)


if __name__ == "__main__":
    main()
