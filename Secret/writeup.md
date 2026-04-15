# Secret Writeup - by Thammanant Thamtaranon

**Secret** is an **Easy**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- The engagement began with a full TCP port scan to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated that ports **22/tcp** (SSH), **80/tcp** (HTTP), and **3000/tcp** (Node.js Express) were open.

---

## Scanning & Enumeration
- Navigating to port 80 and port 3000 in the browser revealed the "DUMB Docs" web application.
  ![Web1.png](Web1.png)
- Further enumeration of the documentation revealed how to interact with the backend API.
  ![Web2.png](Web2.png)
- I tested the API by registering a new user account to see how the application handled authentication.
  ![Web3.png](Web3.png)
  ![Request3.png](Request3.png)
- After successfully registering, I used the Login function to obtain a session token.
  ![Web4.png](Web4.png)
  ![Request4.png](Request4.png)
- I then attempted to access the Private Route, but the application denied access because the account I registered was only a standard user.
  ![Web5.png](Web5.png)
  ![Request5.png](Request5.png)
- Continuing to map out the application, we discovered a hidden path at `/download/files.zip`, which contained the project's source code.
- After downloading and extracting the ZIP file, I noticed it included a `.git` directory. Inspecting the Git commit logs revealed a hardcoded JWT token secret.
  ![JWT_Secret.png](JWT_Secret.png)
- I verified the secret against our existing token using `jwt.io` and confirmed that the secret was valid and actively in use by the server.
  ![Valid_Secret.png](Valid_Secret.png)
- With the signing secret compromised, we now had the ability to forge our own JWTs and elevate our privileges to access the private routes.

---

## Exploitation
- Utilizing a JWT manipulation tool, I forged a new token and changed the `name` parameter in the payload to `theadmin`.
  ![Forge_JWT.png](Forge_JWT.png)
- Sending a request to the private route API with the forged token successfully returned a response, confirming that the application now recognized us as an administrator.
  ![Valid_Forged_JWT.png](Valid_Forged_JWT.png)
- Inspecting the retrieved source code specifically `private.js`, I discovered an additional route at `/logs`. Analyzing the code revealed that it passes user input directly into a system command, leading to a command injection vulnerability.
  ![Route.png](Route.png)
- Sending a GET request to this path required a parameter. Suspecting command injection, I tested the parameter with the payload `;id` to terminate the expected command and inject my own.
  ![Route_Request.png](Route_Request.png)
- The server responded with the output of the `id` command, confirming the injection flaw.
  ![Command.png](Command.png)
- I then crafted a Bash reverse shell payload, sent it through the vulnerable parameter, and successfully caught a reverse shell as the user `dasith`.
  ![Reverse_Shell.png](Reverse_Shell.png)
  ![Dasith.png](Dasith.png)
- Reading the `/etc/passwd` file confirmed that `dasith` was the only standard user on the machine.
  ![PASSWD.png](PASSWD.png)
- To establish a more stable and reliable connection, I generated an SSH key pair, appended my public key to `/home/dasith/.ssh/authorized_keys`, and logged in via SSH. I then captured the `user.txt` flag.
  ![SSH1.png](SSH1.png)
  ![SSH2.png](SSH2.png)
  ![SSH3.png](SSH3.png)

---

## Privilege Escalation
- With a stable SSH shell, I ran `sudo -l` to check for elevated privileges, but I lacked `dasith`'s password.
- I executed `ss -tulpn` to look for listening internal services and discovered a MongoDB instance running locally on port 27017.
  ![Internal_Services.png](Internal_Services.png)
- Connecting to the MongoDB instance using the command-line client, I dumped the database and found a collection of bcrypt password hashes.
  ![Mongo.png](Mongo.png)
- I saved the hashes locally to attempt offline cracking. Unfortunately, while I successfully cracked the password for `newuser`:`mypassword`, I could not crack the hash for `dasith` or `theadmin`. Attempting to use `newuser`'s password to elevate privileges failed.
  ![Hashes.png](Hashes.png)
  ![Cracked.png](Cracked.png)
- Pivoting back to standard Linux enumeration, I searched for files with the SUID bit set and found an interesting custom binary located at `/opt/count`.
  ![SUID.png](SUID.png)
- Checking the `/opt` directory, I also found the source code `code.c` for the binary. Analyzing the C code revealed a critical logic flaw: the program executes as `root` due to the SUID bit while calculating file statistics, and only drops its privileges *after* it prompts the user to save the results.
  ![Code.png](Code.png)
- If we tell the program to read a file that only `root` can access, the program successfully opens it because it hasn't dropped privileges yet. When it prompts us asking if we want to save the results, the process is paused. If we suspend the process in the background using `Ctrl+Z`, the file descriptor remains open. We can then navigate to `/proc/<PID>/fd/` and read the contents of the open file descriptor.
- I ran the `/opt/count` binary against the `/root` directory to map out its contents, which revealed the existence of a `.viminfo` file.
- I ran the binary again, this time pointing it directly at `/root/.viminfo`. When prompted to save, I hit `Ctrl+Z` to suspend the process.
  ![Priv_Esc1.png](Priv_Esc1.png)
- I found the process ID using `pidof count` (e.g., 2153) and used `cat /proc/2153/fd/3` to read the open file descriptor.
  ![Priv_Esc2.png](Priv_Esc2.png)
- Amazingly, the `.viminfo` file contained copied text from a previous Vim session, which included the full plaintext RSA private SSH key for the `root` user!
  ![Priv_Esc3.png](Priv_Esc3.png)
- I copied the private key, saved it to a file on my attacking machine, restricted its permissions using `chmod 600`, and successfully SSH'd into the machine as `root`. Finally, I captured the `root.txt` flag.
  ![Root.png](Root.png)
