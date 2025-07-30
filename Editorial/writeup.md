# Editorial Writeup - by Thammanant Thamtaranon  
- Editorial is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- We began by performing a full TCP port scan with version detection and OS fingerprinting using the command:  
  `nmap -A -T4 -p- 10.10.11.23`  
![Nmap_Scan](Nmap_Scan.png)  
- We added `permx.htb` to our `/etc/hosts` file to enable hostname resolution.

## Scanning & Enumeration  
- We enumerated web directories using:  
  `dirsearch -u http://10.10.11.23`  
![Dirsearch_Scan1](Dirsearch_Scan1.png)  

## Exploitation  

### Privilege Escalation:
