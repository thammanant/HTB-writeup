# Epsilon Writeup - by Thammanant Thamtaranon

**Epsilon** is a **Medium**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- We started the engagement with a full TCP port scan using Nmap to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated the following open ports:
  * **22/tcp:** SSH (OpenSSH 8.2p1 Ubuntu)
  * **80/tcp:** HTTP (Apache httpd 2.4.41)
  * **5000/tcp:** HTTP (Werkzeug httpd 2.0.2 / Python 3.8.10)

---

## Scanning & Enumeration
- The Nmap scan showed an exposed `.git` directory on port 80, so we used `git-dumper` to download the repository to my local machine.
  ![Git.png](Git.png)
- Reviewing the commit history using `git log -p`, we found the virtual host `cloud.epsilon.htb`. I added both `epsilon.htb` and `cloud.epsilon.htb` to my `/etc/hosts` file.
  ![Git_Log1.png](Git_Log1.png)
- Scrolling further down the logs, we discovered a set of AWS access keys and noted them down for later.
  ![Git_Log2.png](Git_Log2.png)
- Reviewing the remaining files, we found the server's source code, indicating it uses the Flask framework and authenticates users via JSON Web Tokens (JWT).
  ![Server_Code1.png](Server_Code1.png)
- We identified the `/home`, `/track`, and `/order` endpoints. The source code showed us that `/order` renders a template. Since this is a Flask application, the underlying template engine is Jinja2.
  ![Server_Code2.png](Server_Code2.png)
- Visiting port 80 in the browser returned a `403 Forbidden` error.
  ![Port80.png](Port80.png)
- Moving on to port 5000, we found a web application called "Epsilon Costume Shop". I tried default credentials like `admin:admin`, but they were unsuccessful.
  ![Port5000.png](Port5000.png)
- Using the leaked AWS keys, I configured my local AWS CLI.
  ![AWS_Config.png](AWS_Config.png)
- I attempted to list the Lambda functions but kept receiving a `500 Internal Server Error`. After some research, we learned this might be a common bug or restriction with the user's permissions. I bypassed this by targeting the intended function name directly, which was `custome_shop_v1`.
  ![AWS_List_Lambda_Function_Failed.png](AWS_List_Lambda_Function_Failed.png)
- Using the `get-function` command, we retrieved the Lambda function details.
  ![AWS_Lambda_Function.png](AWS_Lambda_Function.png)
- This provided a presigned URL, allowing us to download the Lambda function's source code.
  ![AWS_Code.png](AWS_Code.png)
- After extracting and reading the code, we successfully discovered the hardcoded JWT secret.
  ![JWT_Secret.png](JWT_Secret.png)

---

## Exploitation
- With the secret in hand, we could use the server code to forge a valid JWT for the `admin` user.
  ![Forge_JWT.png](Forge_JWT.png)
  ![Forged_JWT.png](Forged_JWT.png)
- I navigated back to the web application on port 5000 and added the forged token to my session cookies.
  ![Add_Cookie.png](Add_Cookie.png)
- Refreshing the `/home` page granted us access to the admin dashboard.
  ![Home.png](Home.png)
- Recalling that the `/order` endpoint uses Jinja2 templates, we tested it for Server-Side Template Injection (SSTI) and confirmed it was vulnerable.
  ![SSTI_ID.png](SSTI_ID.png)
- I generated a bash reverse shell payload and injected it via the SSTI vulnerability.
  ![Payload1.png](Payload1.png)
  ![Payload2.png](Payload2.png)
  ![Payload3.png](Payload3.png)
- We successfully caught the reverse shell on our listener, gaining access as the user `tom`, and captured the `user.txt` flag.
  ![Tom.png](Tom.png)

---

## Privilege Escalation
- Running `sudo -l` required a password, which we didn't have. Checking the `/etc/passwd` file revealed that `tom` is the only standard user on the machine, meaning we can likely escalate straight to root from here.
  ![PASSWD.png](PASSWD.png)
- After further local enumeration yielded nothing, I transferred `pspy64` to the machine to monitor background processes.
  ![PSPY64_1.png](PSPY64_1.png)
  ![PSPY64_2.png](PSPY64_2.png)
  ![PSPY64_3.png](PSPY64_3.png)
- The output showed us that a script at `/usr/bin/backup.sh` runs regularly via a cron job, so I read the contents of the file.
  ![Backup.png](Backup.png)
- The script creates an archive of the `/var/www/app/` directory in `/opt/backups/`, calculates its SHA1 checksum, and saves the hash to a file named `/opt/backups/checksum`. It then sleeps for 5 seconds before creating a final archive in `/var/backups/web_backups/` that includes the `checksum` file, and finally clears the `/opt/backups/` directory.
- Checking the permissions on `/opt/backups/`, we found that the directory is writable by the user `tom`. Because the script sleeps for 5 seconds between creating the `checksum` file and archiving it into the final backup, it is vulnerable to a Time-of-Check to Time-of-Use (TOCTOU) race condition. By replacing the `checksum` file with a symbolic link pointing to `/root` during this 5-second window, we can force the final `tar` command to follow the symlink and archive the entire `/root` directory.
  ![Writable.png](Writable.png)
- I wrote a bash script to automate this race condition for us. The script continuously removes the `checksum` file and creates a symlink pointing to `/root` in its place. Simultaneously, it monitors `/var/backups/web_backups/` for a new backup archive. Once a new backup appears, the script terminates the symlink loop, extracts the latest archive to `/tmp`, and outputs the `/root/.ssh/id_rsa` key from the extracted contents.
  ![Script.png](Script.png)
  ![Run_Script.png](Run_Script.png)
- Using the extracted private key, we connected to the machine via SSH as `root` and captured the `root.txt` flag.
  ![Root.png](Root.png)
