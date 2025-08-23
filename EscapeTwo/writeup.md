# EscapeTwo Writeup - by Thammanant Thamtaranon  
- EscapeTwo is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.11.51`  
![Nmap_Scan1](Nmap_Scan1.png)
![Nmap_Scan2](Nmap_Scan2.png) 
- The scan revealed a Windows Active Directory Domain Controller with multiple key services open, including:
  - 53/tcp (DNS): Domain Name Service
  - 88/tcp (Kerberos): Authentication protocol\
  - 135/tcp (MSRPC): Microsoft Remote Procedure Call
  - 139/445/tcp (SMB): File sharing and network communication
  - 389/636/tcp (LDAP/S): Lightweight Directory Access Protocol (and SSL)
  - 1433/tcp (MSSQL): Microsoft SQL Server <-- High Value Target
  - 5985/tcp (WinRM): Windows Remote Management
  
- I added `DC01.sequel.htb` and `sequel.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- Since we have been given the credential `rose / KxEPkKe6R8su`, we will try use this with smb:  `smbclient -L //10.10.11.51 -U rose`
![SMB](SMB.png) 
- After enumerate all files and directories, we found nothing of use.
- Next we will try connect to MSSQL:  
## Exploitation  


## Privilege Escalation  
