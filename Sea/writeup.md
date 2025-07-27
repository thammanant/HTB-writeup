# Sea Writeup - by Thammanant Thamtaranon
  - Sea is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance
  - Initially, we performed a full TCP port scan with version detection and OS fingerprinting using the command:  
    `nmap -A -T4 -p- 10.10.11.32`  
![Nmap_Scan](Nmap_Scan.png)

  - We added `sightless.htb` to our `/etc/hosts` file to enable hostname resolution for easier access.

## Scanning & Enumeration
  - We enumerated web directories using:  
    `dirsearch -u http://10.10.11.32`  
    but no interesting paths were found.  

## Exploitation
  
