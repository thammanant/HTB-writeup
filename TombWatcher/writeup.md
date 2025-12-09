# TombWatcher Writeup - by Thammanant Thamtaranon

**TombWatcher** is an medium-difficulty Windows machine hosted on Hack The Box.

## Reconnaissance
- I began with a full TCP port scan, including service/version detection and OS fingerprinting:
  `nmap -A -T4 -p- 10.10.11.72`
  ![Nmap_Scan](Nmap_Scan.png)
- The scan revealed the following open ports:
  - **53** — DNS (Simple DNS Plus)
  - **80** — HTTP (Microsoft IIS httpd 10.0)
  - **88** — Kerberos (Microsoft Windows Kerberos)
  - **135** — MSRPC (Microsoft Windows RPC)
  - **139** — NetBIOS-SSN
  - **389** — LDAP (Microsoft Windows Active Directory LDAP)
  - **445** — Microsoft-DS (SMB)
  - **464** — kpasswd
  - **593** — RPC over HTTP (Microsoft Windows RPC over HTTP 1.0)
  - **636** — LDAPS (SSL/LDAP)
  - **3268** — Global Catalog LDAP
  - **3269** — Global Catalog LDAPS
  - **5985** — WinRM (Microsoft HTTPAPI httpd 2.0)
  - **9389** — AD Web Services (.NET Message Framing)
  - **49666** - 49720 — RPC High Ports (Microsoft Windows RPC)
- I added `tombwatcher.htb` and `dc01.tombwatcher.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration


## Exploitation


## Privilege Escalation
