# Library Import
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from matchdto import MatchInfo
from botocore.exceptions import ClientError
import boto3
import os
import json
import logging
import time
import traceback

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.timestamp() * 1000
    raise TypeError ("Type %s not serializable" % type(obj))


def __serverless_chrome_options__(browser_binary):
    _options = Options()
    _options.binary_location = browser_binary
    _options.add_argument('--headless')
    _options.add_argument('--no-sandbox')
    _options.add_argument('--window-size=1280,1024')
    _options.add_argument("--hide-scrollbars")
    _options.add_argument("--enable-logging")
    _options.add_argument("--disable-application-cache")
    _options.add_argument("--disable-infobars")
    _options.add_argument('--disable-dev-shm-usage')
    _options.add_argument('--disable-gpu')
    _options.add_argument('--single-process')
    _options.add_argument("--ignore-certificate-errors")
    return _options


def __serverless_chrome__(browser_binary, selenium_binary):
    _options = __serverless_chrome_options__(browser_binary)
    _driver = webdriver.Chrome(executable_path=selenium_binary, options=_options)
    _driver.set_page_load_timeout(20)
    return _driver

def handler(event=None, context=None):
    browserBinary = "/opt/headless-chromium"
    seleniumBinary = "/opt/chromedriver"
    targetUrl = "http://live.titan007.com/index2in1_big.aspx?id=3"
    bucketName = os.getenv('BUCKETNAME')
    print("Bucket: ", bucketName)

    driver = None
    try:
        driver = __serverless_chrome__(browserBinary, seleniumBinary)
        driver.get(targetUrl)
        time.sleep(3)

        raw_a = driver.execute_script("return JSON.stringify(A);")
        raw_data = driver.execute_script("return JSON.stringify(sData);")
        raw_data_json = json.loads(raw_data)
        raw_a_json = json.loads(raw_a)

        # Parse Web JS Object
        match_dto_objects = []
        raw_odd_limit = 9
        if isinstance(raw_a_json, list):
            for match_info in raw_a_json:
                if match_info is not None:
                    match = MatchInfo(match_info)
                    if match.id in raw_data_json:
                        raw_odd_data = raw_data_json[match.id]
                        for raw_data in raw_odd_data:
                            # Append X (raw_odd_limit) items into array
                            while len(raw_data) < raw_odd_limit:
                                raw_data.append(None)
                        match.set_raw_odds(raw_odd_data)
                    match_dto_objects.append(match)

        # Define Output Variables
        pre_matches = []
        pre_matches_hl = []
        inplay_matches = []
        inplay_matches_hl = []
        ft_matches = []
        core_data = []
        result = {}

        for match in match_dto_objects:
            core_data.append(match.all_attributes)
            if match.status > 0:
                if match.asian_odds_diff_from_initial or match.ls_odds_diff_from_initial:
                    inplay_matches_hl.append(match.all_attributes)
                else:
                    inplay_matches.append(match.all_attributes)
            elif match.status < 0:
                ft_matches.append(match.all_attributes)
            else:
                __delta__ = match.actual_date - datetime.now()
                __minute_diff__ = abs(int(__delta__.total_seconds() / 60))
                if __minute_diff__ <= 30 and (match.asian_odds_diff_from_initial or match.ls_odds_diff_from_initial):
                    pre_matches_hl.append(match.all_attributes)
                else:
                    pre_matches.append(match.all_attributes)

        result["IPData"] = inplay_matches
        result["IPHLData"] = inplay_matches_hl
        result["FTData"] = ft_matches
        result["preMatchesHLData"] = pre_matches_hl
        result["preMatchesData"] = pre_matches
        result["data"] = core_data
        result["lastModified"] = datetime.now().timestamp() * 1000
        result["success"] = True

        jsonFile = "data.json"
        tmpJsonFile = "/tmp/"+jsonFile
        print(json.dumps(result, default=json_serial), file=open(tmpJsonFile, "w"))
        uploaded = upload_file(tmpJsonFile, bucketName, jsonFile)

        return {
            'statusCode': 200,
            'body': "Extracted Data Json and Uploaded to S3 Successfully"
        }

    except Exception as err:
        traceback.print_exc()
        return err

    finally:
        if driver is not None:
            driver.quit()


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    handler()
