# Photobomb Writeup - by Thammanant Thamtaranon  
- Photobomb is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting using the command:  
  `nmap -A -T4 -p- 10.10.11.182`  
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed two open ports:
  - 22 (SSH)
  - 8080 (HTTP).
- I added `analytical.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I ran a directory brute-force using `dirsearch` with `dirsearch -u 10.10.11.204:8080` and discovered the `/upload` path. When I uploaded a file there, it returned a link to view the uploaded image, which used the path `show_image?img=`.  
![Dirsearch_Scan](Dirsearch_Scan.png)  

## Exploitation  


## Privilege Escalation  
- I attempted to run `sudo -l`, but Phil did not have sudo privileges.  
