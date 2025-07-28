# Sea Writeup - by Thammanant Thamtaranon
  - Sea is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance
  - Initially, we performed a full TCP port scan with version detection and OS fingerprinting using the command:  
    `nmap -A -T4 -p- 10.10.11.28`  
![Nmap_Scan](Nmap_Scan.png)

## Scanning & Enumeration
  - We enumerated web directories using `dirsearch -u http://10.10.11.28`.
![Dirsearch_Scan](Dirsearch_Scan.png)

## Exploitation
  - We found `/contact.php`.
![Contact](Contact.png)
  - We then try sent out link in website, and the admin click the link.
![Test](Test.png)
  - 
  
