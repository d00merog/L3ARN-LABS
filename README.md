# L3ARN-LABS
ᴛʜᴇ ꜰᴜᴛᴜʀᴇ ᴡᴀɪᴛꜱ ꜰᴏʀ ɴᴏ ᴏɴᴇ. ʟᴇᴠᴇʟ ᴜᴘ ʏᴏᴜʀ ꜱᴋɪʟʟꜱ ɴᴏᴡ. ᴊᴏɪɴ ᴏᴜʀ ʟᴇᴀʀɴɪɴɢ ʜᴜʙ 🍎 | ʙʀɪɴɢɪɴɢ ᴛʜᴇ ʟᴀʏᴇʀ 3 ᴏꜰ ᴇᴅᴜᴄᴀᴛɪᴏɴ

![351919820-309d5534-f15a-4872-a854-f3fbd5f28e1c](https://github.com/user-attachments/assets/8b673575-b861-42f7-8b9e-a6a145ec24b1)

## Secrets management

Application secrets are no longer stored in a local `.env` file. Configure a self-hosted HashiCorp Vault and provide `VAULT_ADDR` and `VAULT_TOKEN` environment variables (or Docker secrets) when running the application. Secrets are looked up from Vault at `l3arn-labs/<SECRET_NAME>` and fallback to values in `/run/secrets/<SECRET_NAME>` or environment variables.

## Pre-commit hooks

This repository uses [pre-commit](https://pre-commit.com/) with `detect-secrets` to scan for secrets before every commit.

Install the hooks after cloning:

```bash
pip install pre-commit
pre-commit install
```

