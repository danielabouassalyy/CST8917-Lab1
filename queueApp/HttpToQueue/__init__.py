import logging
import azure.functions as func

def main(req: func.HttpRequest, outputQueueItem: func.Out[str]) -> func.HttpResponse:
    logging.info("HTTP trigger received a request; sending message to queue.")

    # grab msg from query string or JSON body
    msg = req.params.get("msg")
    if not msg:
        try:
            body = req.get_json()
            msg = body.get("msg")
        except ValueError:
            pass

    # default if still empty
    if not msg:
        msg = "Hello from Lab1!"

    # write to queue
    outputQueueItem.set(msg)

    return func.HttpResponse(f"Queued: {msg}", status_code=200)
