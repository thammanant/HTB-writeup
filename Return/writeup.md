# Return Writeup - by Thammanant Thamtaranon  
- Return is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:
```bash
nmap -A -T4 -p- 10.10.10.152
```
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed multiple open ports:  
  - 21 (FTP)  
  - 80 (HTTP)  
  - 135 (MSRPC)  
  - 139 (NETBIOS)  
  - 445 (SMB)  
  - 5985 (HTTP)

## Scanning & Enumeration 

## Exploitation  
