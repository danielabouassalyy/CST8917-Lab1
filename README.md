## Clone Your Repo & Create a Python venv

```bash
git clone https://github.com/<username>/CST8917-Lab1.git
cd CST8917-Lab1
mkdir queueApp && cd queueApp
py -3.11 -m venv .venv
```

## Activate the venv:
## PowerShell:
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

