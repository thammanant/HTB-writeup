# Aero Writeup - by Thammanant Thamtaranon

**Aero** is a **Medium**-difficulty Windows machine hosted on Hack The Box.

---

## Reconnaissance
- We began the engagement with a full TCP port scan using Nmap to identify open services and fingerprint the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The notable open port on the machine was:
  * **80/tcp:** HTTP (Microsoft IIS httpd 10.0)

---

## Scanning & Enumeration
- Visiting port 80 revealed a Windows 11 theme repository featuring a file upload function.
  ![Port80.png](Port80.png)
- We tested various Windows theme extensions by creating dummy files to determine which file types the application permitted.
  ![Extension1.png](Extension1.png)
- The upload mechanism only accepted `.theme` and `.themepack` files.
  ![Extension2.png](Extension2.png)
- Researching vulnerabilities associated with these extensions led us to ThemeBleed (CVE-2023-38146).
  - This Remote Code Execution (RCE) vulnerability allows weaponized `.theme` or `.themepack` files to trick Windows into accessing an attacker-controlled SMB share. By supplying a malformed version number (such as "999") inside the theme file, a race condition is triggered during `.msstyles` file handling, causing the system to load a malicious DLL instead of a verified one.
  ![ThemeBleed1.png](ThemeBleed1.png)

---

## Exploitation
- We utilized a publicly available Proof of Concept (PoC) from [GitHub](https://github.com/Jnnshschl/CVE-2023-38146) to exploit the ThemeBleed vulnerability.
  ![ThemeBleed2.png](ThemeBleed2.png)
- We executed the PoC script to generate our malicious theme payload, host the rogue SMB server, and set up a Netcat listener to catch the incoming connection.
  ![ThemeBleed3.png](ThemeBleed3.png)
- We then uploaded the generated `.theme` file to the web application (noting that the `.themepack` extension failed to process).
  ![ThemeBleed4.png](ThemeBleed4.png)
- Shortly after the upload, the target server connected back to our SMB server and successfully authenticated to request the malicious DLL.
  ![ThemeBleed5.png](ThemeBleed5.png)
- Our listener caught the reverse connection, granting us a shell as the user `sam.emerson`, allowing us to capture the user flag.
  ![Sam.png](Sam.png)
  
---

## Privilege Escalation
- During post-exploitation enumeration, we discovered a document within the `sam.emerson` user's Documents folder.
  ![Document.png](Document.png)
- We downloaded this document to our local machine for further analysis.
  ![Downloaded.png](Downloaded.png)
- Reviewing the PDF revealed a security advisory stating that the machine's infrastructure was vulnerable to CVE-2023-28252, a critical privilege escalation flaw within the Windows Common Log File System (CLFS) driver.
  ![PDF.png](PDF.png)
- Because the manual exploit chain for this CVE is highly complex, we opted to use Metasploit. First, we upgraded our standard reverse shell to a Meterpreter session. (If you are interested in the exploit chain, visit this [Github](https://github.com/fortra/CVE-2023-28252))
  ![Meterpreter1.png](Meterpreter1.png)
  ![Meterpreter2.png](Meterpreter2.png)
  ![Meterpreter3.png](Meterpreter3.png)
- Once the Meterpreter session was established, we backgrounded it and searched Metasploit for the corresponding CVE module.
  ![CVE1.png](CVE1.png)
- We configured the module with the appropriate session ID, `LHOST`, and `LPORT`, and executed the exploit.
  ![CVE2.png](CVE2.png)
- The exploit successfully injected the payload, dropping us into an interactive shell as `NT AUTHORITY\SYSTEM`, where we secured the root flag.
  ![NT_AUTHORITY.png](NT_AUTHORITY.png)
