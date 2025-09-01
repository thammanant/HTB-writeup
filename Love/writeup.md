# Love Writeup - by Thammanant Thamtaranon  
- Love is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:
```bash
nmap -A -T4 -Pn -p- 10.10.10.239
```
![Nmap_Scan1](Nmap_Scan1.png)  
![Nmap_Scan2](Nmap_Scan2.png)  
- The scan showed multiple open ports:  
  - 53 (DNS)  
  - 88 (Kerberos)  
  - 135, 139, 445 (MSRPC, NetBIOS, SMB)  
  - 389, 636, 3268, 3269 (LDAP / LDAPS / Global Catalog)  
  - 464 (kpasswd5)  
  - 593 (RPC)  
  - 5985 (WinRM)  

- I added `cicada.htb` and `CICADA-DC.cicada.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  



## Exploitation  


## Privilege Escalation  
