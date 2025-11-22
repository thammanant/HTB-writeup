# Strutted Writeup - by Thammanant Thamtaranon  
- Strutted is an medium Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.11.59`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP   
- I added `strutted.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  


## Exploitation  


## Privilege Escalation  

