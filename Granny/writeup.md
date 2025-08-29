# Granny Writeup - by Thammanant Thamtaranon  
- Granny is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:
```bash 
nmap -A -T4 -p- 10.10.10.15
```
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed one open port:  
  - 80 (HTTP)  

## Scanning & Enumeration  


## Privilege Escalation  
- We ran `whoami /priv` and `whoami /groups` but found nothing useful.  
