import sys, base64, json
from traceback import format_exc



def get_argv(logging) -> dict:
    try:
        if len(sys.argv) == 2:
            input_ = sys.argv[1] # get parameter
            input_ = base64.b64decode(input_).decode("utf-8") # decode base64
            input_ = json.loads(input_) # Convert string to json format
            logging.info(f"input = {input_}")

            return input_
        else:
            logging.error("No input parameters.")
    except:
        logging.error(format_exc())



def error(logging, message: str, time: str) -> dict:
    logging.error(message)
    result = {
        "status": "fail",
        "time":   time,
        "reason": message
        }
    
    return result