# Active Writeup - by Thammanant Thamtaranon  
- Active is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:
```bash
nmap -A -T4 -Pn -p- 10.10.10.100
```
![Nmap_Scan1](Nmap_Scan1.png)  
![Nmap_Scan2](Nmap_Scan2.png)  
- The scan showed multiple open ports:  
  - 80 (HTTP)  
  - 135, 139, 445 (MSRPC, SMB, NetBIOS)  
  - 443 (HTTPS)  
  - 3306 (MySQL)  
  - 5000 (HTTP)  
  - 5985, 5986 (WinRM HTTP, WinRM HTTPS)

- I added `staging.love.htb` and `love.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- We ran a directory brute-force using `gobuster`:
```bash 
gobuster dir -u love.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -t 50
```
![Gobuster](Gobuster.png)  
- The interesting path is `/admin`. We tried common credentials, but they did not work.  
- The `index.php` page requires a voting ID and password, so we moved on.  
- We tried connecting to port 5000 but got `Forbidden`.  
- Visiting `http://staging.love.htb` revealed a Free File Scanner service. We navigated to the demo and found a URL parameter.  
- We attempted SSRF to port 5000 and it worked, revealing Admin's password.  
![SSRF](SSRF.png)  
- We used the credential `admin:@LoveIsInTheAir!!!!` at `/admin` and successfully logged in.

## Exploitation  


## Privilege Escalation  
