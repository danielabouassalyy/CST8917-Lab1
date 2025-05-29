## Clone Your Repo & Create a Python venv

```bash
git clone https://github.com/<username>/CST8917-Lab1.git
cd CST8917-Lab1
mkdir queueApp && cd queueApp
py -3.11 -m venv .venv
```

## Activate the venv:
```bash
. .\.venv\Scripts\Activate.ps1
```
## Install Azure Functions SDK & Create Host Files
```bash
echo azure-functions > requirements.txt
pip install azure-functions

cat > host.json << 'EOF'
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[2.*, 3.0.0)"
  }
}
EOF

cat > local.settings.json << 'EOF'
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your_storage_conn_string>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SqlConnectionString": "Server=tcp:lab1sqlsrv.database.windows.net,1433;Database=lab1db;User ID=lab1admin;Password=P@ssw0rd123!;Encrypt=true"
  }
}
EOF

```

## Scaffold the Storage-Queue Function
```bash
func init . --worker-runtime python
func new --name HttpToQueue --template "HTTP trigger" --authlevel function

```
## Add the Storage Queue output binding
Edit HttpToQueue/function.json, replacing its "bindings" array with:
```bash
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get","post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    },
    {
      "name": "outputQueueItem",
      "type": "queue",
      "direction": "out",
      "queueName": "lab1-output-queue",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```
## Implement the function logic
Replace HttpToQueue/__init__.py with:****
```bash
import azure.functions as func

def main(req: func.HttpRequest, outputQueueItem: func.Out[str]) -> func.HttpResponse:
    msg = req.params.get("msg") or (req.get_json(silent=True) or {}).get("msg") or "Hello from Lab1!"
    outputQueueItem.set(msg)
    return func.HttpResponse(f"Queued: {msg}", status_code=200)
```
## Commit your Queue function

```bash
git add HttpToQueue/function.json HttpToQueue/__init__.py
git commit -m "✅ Scaffolded Storage Queue function with output binding"
```
## Provision Azure resources for your Queue function

```bash
az login
az group create --name lab1-rg --location canadaeast
az storage account create --name lab1store12345 --resource-group lab1-rg --location canadaeast --sku Standard_LRS
az functionapp create `
  --name lab1-queue-func `
  --resource-group lab1-rg `
  --storage-account lab1store12345 `
  --os-type Linux `
  --runtime python `
  --functions-version 4 `
  --consumption-plan-location canadaeast
```
## Deploy the Queue function to Azure
```bash
. .\.venv\Scripts\Activate.ps1
func azure functionapp publish lab1-queue-func
```
## Test & verify your Queue function
```bash
# grab its function key
funcKey=$(az functionapp function keys list \
  --resource-group lab1-rg \
  --name lab1-queue-func \
  --function-name HttpToQueue \
  --query default -o tsv)

# invoke it
curl "https://lab1-queue-func.azurewebsites.net/api/HttpToQueue?code=$funcKey&msg=QueueTest"

# verify in your storage queue
az storage queue peek --account-name lab1store12345 --name lab1-output-queue --num-messages 5
```



