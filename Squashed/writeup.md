# Squashed Writeup - by Thammanant Thamtaranon  
- Squashed is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.11.233`  
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed two open ports:  
  - 22 (SSH)  
  - 80 (HTTP)  
- I added `analytical.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I ran a directory brute-force using `dirsearch`:  
  `dirsearch -u http://analytical.htb`  
![Dirsearch_Scan](Dirsearch_Scan.png)  
- No interesting directories were found.

- I then enumerated virtual hosts using `ffuf`:  
  `ffuf -u http://analytical.htb -H "Host: FUZZ.analytical.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`  
![VHost](VHost.png)  
- I discovered `data.analytical.htb`, so I added that to `/etc/hosts` as well.

- Visiting `http://data.analytical.htb/` redirected to the login page:  
  `http://data.analytical.htb/auth/login?redirect=%2F`

## Exploitation  


## Privilege Escalation  
