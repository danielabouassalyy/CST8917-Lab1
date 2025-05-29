[Lab 1 Demo Video](https://youtu.be/1cbL3N006t8?si=BN40SQUYEXn3x-ul)
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
## Scaffold the Azure SQL function
```bash

# From queueApp folder
func new --name HttpToSql --template "HTTP trigger" --authlevel function
```

## Add the SQL output binding
Edit HttpToSql/function.json and replace its "bindings" with:
```bash

{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get","post"],
      "route": "sql"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    },
    {
      "name": "outputRecord",
      "type": "sql",
      "direction": "out",
      "connectionStringSetting": "SqlConnectionString",
      "tableName": "Messages"
    }
  ]
}

```
## Implement the SQL function code
Replace HttpToSql/__init__.py with:
```bash

import azure.functions as func

def main(req: func.HttpRequest, outputRecord: func.Out[func.SqlRow]) -> func.HttpResponse:
    text = req.params.get("msg") or (req.get_json(silent=True) or {}).get("msg") or "Hello SQL"
    outputRecord.set(func.SqlRow({"Text": text}))
    return func.HttpResponse(f"Inserted: {text}", status_code=200)

```
## Provision your Azure SQL server & database
```bash
# (No venv needed)
az sql server create `
  --name lab1sqlsrv `
  --resource-group lab1-rg `
  --location canadacentral `
  --admin-user lab1admin `
  --admin-password "P@ssw0rd123!"

az sql db create `
  --resource-group lab1-rg `
  --server lab1sqlsrv `
  --name lab1db `
  --service-objective S0


```
## Open firewall & create the Messages table

```bash
az sql server firewall-rule create `
  --resource-group lab1-rg `
  --server lab1sqlsrv `
  --name AllowMyIP `
  --start-ip-address <your_ip> `
  --end-ip-address <your_ip>
# and/or:
az sql server firewall-rule create -g lab1-rg -s lab1sqlsrv -n AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

## In the Azure Portal, go to lab1sqlsrv → Databases → lab1db → Query editor (preview), sign in, and run:
```bash

CREATE TABLE Messages (
  Id    INT IDENTITY(1,1) PRIMARY KEY,
  Text  NVARCHAR(200)
);

```
## Wire up your Function App & deploy the SQL function
```bash
# Configure your Function App with the DB connection string
az functionapp config appsettings set \
  --name lab1-queue-func \
  --resource-group lab1-rg \
  --settings SqlConnectionString="Server=tcp:lab1sqlsrv.database.windows.net,1433;Database=lab1db;User ID=lab1admin;Password=P@ssw0rd123!;Encrypt=true"

# Publish both functions (from queueApp with venv active)
func azure functionapp publish lab1-queue-func
```

## Test your SQL function end-to-end
```bash

# Grab the SQL function’s key
sqlKey=$(az functionapp function keys list \
  --resource-group lab1-rg \
  --name lab1-queue-func \
  --function-name HttpToSql \
  --query default -o tsv)

# Invoke it
curl "https://lab1-queue-func.azurewebsites.net/api/sql?code=$sqlKey&msg=TestSQL"
# Expect: Inserted: TestSQL

# Confirm in the database (Portal Query Editor or):
az sql db show-connection-string \
  --client ado.net \
  --name lab1db \
  --server lab1sqlsrv
# Then use your favorite SQL client to SELECT * FROM Messages;
```
## Commit and push your SQL function changes
```bash
cd queueApp
git add HttpToSql/function.json HttpToSql/__init__.py
git commit -m "✅ Azure SQL function deployed and verified"
git push

```

