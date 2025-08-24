# Blue Writeup - by Thammanant Thamtaranon  
- Blue is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.10.40`  
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed two open ports:  
  - 135 (MSRPC) 
  - 139 (NetBIOS-SSN)
  - 445 (SMB) 

## Scanning & Enumeration  


## Exploitation  


## Privilege Escalation  
