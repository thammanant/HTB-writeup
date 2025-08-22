# Shoppy Writeup - by Thammanant Thamtaranon  
- Shoppy is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting using the command:  
  `nmap -A -T4 -p- 10.10.11.182`  
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed two open ports:
  - 22 (SSH)
  - 80 (HTTP)
- We then added `Shoppy.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I ran a directory brute-force using `dirsearch`: `dirsearch -u Shoppy.htb`  
![Dirsearch_Scan](Dirsearch_Scan.png)  
- I then enumerated virtual hosts using `ffuf`:  
  `ffuf -u http://photobomb.htb -H "Host: FUZZ.photobomb.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`  


## Exploitation  


## Privilege Escalation  
