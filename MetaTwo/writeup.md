# MetaTwo Writeup - by Thammanant Thamtaranon  
- MetaTwo is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.11.186`  
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed two open ports:  
  - 22 (SSH)  
  - 80 (HTTP)  
- I then added `stocker.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I ran a directory brute-force using `dirsearch`:  
  `dirsearch -u http://stocker.htb`  
![Dirsearch_Scan](Dirsearch_Scan.png)  
- No interesting directories were found.

- I then enumerated virtual hosts using `ffuf`:  
  `ffuf -u http://stocker.htb -H "Host: FUZZ.stocker.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`  
![VHost](VHost.png)  
- From this, I discovered `dev.stocker.htb` and added it to `/etc/hosts`.

- Visiting `http://dev.stocker.htb` redirected me to the login page:  
  `http://dev.stocker.htb/login`
- Using Wappalyzer, I identified Node.js and Express framework.
- We also noticed the `© 2022`, which suggested the latest update was in 2022.

## Exploitation  

## Privilege Escalation  
