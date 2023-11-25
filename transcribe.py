import logging
import yaml
import requests
import time

#Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    LANG = config["lang"]
    headers = {"keyId": config["KeyId"], "keySecret": config["KeySecret"]}
RESULT_TYPE = 4

def create(wav_file_path: str) -> str:
    create_data = {"lang": LANG}
    files = {}
    create_url = "https://api.speechflow.io/asr/file/v1/create"

    try:
        if wav_file_path.startswith('http'):
            create_data['remotePath'] = wav_file_path
            logger.info('Submitting a remote file')
            response = requests.post(create_url, data=create_data, headers=headers)
        else:
            logger.info('Submitting a local file')
            create_url += "?lang=" + LANG
            files['file'] = open(wav_file_path, "rb")
            response = requests.post(create_url, headers=headers, files=files)

        response.raise_for_status()
        create_result = response.json()
        logger.info(create_result)

        if create_result["code"] == 10000:
            return create_result["taskId"]
        else:
            logger.error("Create error: %s", create_result["msg"])
            return ""

    except requests.RequestException as e:
        logger.error("Create request failed: %s", e)
        return ""

def query(task_id: str) -> dict:
    query_url = f"https://api.speechflow.io/asr/file/v1/query?taskId={task_id}&resultType={RESULT_TYPE}"
    logger.info('Querying transcription result')

    while True:
        try:
            response = requests.get(query_url, headers=headers)
            response.raise_for_status()
            query_result = response.json()

            if query_result["code"] == 11000:
                logger.info('Transcription result obtained')
                return query_result
            elif query_result["code"] == 11001:
                logger.info('Waiting for transcription result')
                time.sleep(3)
                continue
            else:
                logger.error("Transcription error: %s", query_result['msg'])
                break

        except requests.RequestException as e:
            logger.error("Query request failed: %s", e)
            break

    return query_result

def transcribe_audio(wav_file_path: str) -> str:
    task_id = create(wav_file_path)
    if not task_id:
        return "Error creating transcription task"

    query_result = query(task_id)
    if query_result.get("code") == 11000:
        return query_result.get("result", "No transcription result found")
    else:
        return "Error querying transcription result"