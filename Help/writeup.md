# Help Writeup - by Thammanant Thamtaranon  
- Help is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.10.121`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed three open ports:  
  - **22** — SSH  
  - **80** — HTTP  
  - **3000** — HTTP  
- We added `Help.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- We ran Vhost enumeration using  
  `ffuf -u http://help.htb -H "Host: FUZZ.help.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`, but nothing was found.
- Next, we used `dirsearch` on both port 80 and 3000:  
  ![Dirsearch_Scan1](Dirsearch_Scan1.png)  
  ![Dirsearch_Scan2](Dirsearch_Scan2.png)  
  ![Dirsearch_Scan3](Dirsearch_Scan3.png)
- Visiting `http://htb.help/support/` revealed a site using `HelpDeskZ`.  
  ![HelpDeskZ](HelpDeskZ.png)
- Visiting `http://help.htb/support/README.md` confirmed it was running `HelpDeskZ` version 1.0.2.
- Heading over to `http://htb.help:3000`, we discovered a message for user `Shiv`.  
  ![Message](Message.png)
- Checking `http://help.htb:3000/graphql/` showed `GET query missing.`—a solid hint toward a GraphQL API.

## Exploitation  
- We looked up CVEs for `HelpdeskZ 1.0.2` and found two relevant vulnerabilities.  
  ![CVE](CVE.png)
- We attempted the first exploit (Arbitrary File Upload) but it failed.  
  ![Failed](Failed.png)
- We shifted our focus to port 3000.
- After tweaking the request, we fired off a test GraphQL query.  
  ![QueryPOC](QueryPOC.png)
- This confirmed that the API endpoint was active and responding.
- We then used an introspection query:  
  `{
  "query": "query IntrospectionQuery { __schema { queryType { name fields { name type { name } } } mutationType { name fields { name type { name } } } types { name fields { name type { name kind } } } } }"
}`  
  This gave us complete visibility into the internal schema.
- We noticed a `User` data type with `username` and `password` fields.  
  ![API](API.png)
- We updated the query to extract the credentials:  
  `{
  "query": "query { user { username password } }"
}`  
  ![Helpme](Helpme.png)
- We submitted the password to CrackStation and successfully recovered Helme’s password.  
  ![Helpme_Password](Helpme_Password.png)
- With these credentials, we logged into HelpDeskZ.  
  ![Login](Login.png)
- Now authenticated, we moved on to the second exploit.
- After reviewing the vulnerability details, we learned we needed to log in and create a ticket with an attachment.  
  ![POC1](POC1.png)
- The attachment download URL was:  
  `http://help.htb/support/?v=view_tickets&action=ticket&param[]=4&param[]=attachment&param[]=1&param[]=6`  
  We tested for SQLi using:  
  - `...6 and 1=2-- -`  
  - `...6 and 1=1-- -`  
  The first returned an error, while the second worked—confirming SQL injection.  
  ![POC2](POC2.png)
- We saved the request to `req.txt`.  
  ![POC3](POC3.png)
- Running sqlmap with `sqlmap -r req.txt --batch` gave us full database access.  
  ![POC4](POC4.png)  
  ![POC5](POC5.png)  
  ![POC6](POC6.png)
- We eventually recovered the admin credentials.  
  ![Credential](Credential.png)
- Trying SSH with each user, we finally got in as user `help`.  
  ![HELP](HELP.png)
- We captured the user flag.

## Privilege Escalation  
- Running `sudo -l` confirmed we had no sudo permissions.
- Checking `/var/mail`, we found a mail addressed to help.  
  ![Mail](Mail.png)
- The mail was an automated Cron email, but still executed with help’s permissions.
- After several attempts to find misconfigurations, we began considering kernel exploits as a last resort.
- Running `uname -a` revealed the kernel version: Linux 4.4.0-116-generic.
- We found a suitable local privilege escalation: `CVE-2017-16995`.
- We copied the exploit from ExploitDB, compiled it, and executed it—gaining root access.  
  ![Root](Root.png)
- We captured the root flag.
