import azure.functions as func

def main(req: func.HttpRequest, outputRecord: func.Out[func.SqlRow]) -> func.HttpResponse:
    # Try to read ?msg=... or {"msg": "..."} from the body
    text = req.params.get("msg")
    if not text:
        try:
            body = req.get_json()
            text = body.get("msg")
        except ValueError:
            text = None

    # Fallback default
    if not text:
        text = "Hello SQL"

    # Send the record to Azure SQL
    outputRecord.set(func.SqlRow({"Text": text}))

    return func.HttpResponse(f"Inserted: {text}", status_code=200)
