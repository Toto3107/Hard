System Inspection
whoami
hostname
uptime
df -h
free -m


Production use:
First commands run during outage or incident.

🚨 Production Bugs & How to Fix Them
🐞 Bug 1: “Permission denied” Error
❌ Problem

Application fails to write logs:

Permission denied: app.log

🔍 Root Cause

File owned by root

App runs as non-root user

✅ Fix
sudo chown devops:devops app.log
chmod 640 app.log

📌 Production Lesson

90% permission bugs happen due to wrong ownership, not chmod.

🐞 Bug 2: Service Not Running After Reboot
❌ Problem

Service works now, but fails after reboot.

🔍 Root Cause

Service not enabled at startup.

✅ Fix
sudo systemctl enable nginx
sudo systemctl start nginx

📌 Production Lesson

Always enable critical services.

🐞 Bug 3: Server Disk Full (Very Common!)
❌ Problem

Server becomes unresponsive

Apps crash

SSH login slow

🔍 Diagnose
df -h
du -sh /var/log/*

✅ Fix
sudo journalctl --vacuum-time=7d
sudo rm -rf /var/log/*.old

📌 Production Lesson

Disk alerts should be configured before 80%.

🐞 Bug 4: SSH Suddenly Stops Working
❌ Problem

Cannot connect via SSH.

🔍 Diagnose
systemctl status ssh
journalctl -u ssh

✅ Fix
sudo systemctl restart ssh
sudo systemctl enable ssh

📌 Production Lesson

Logs are always more reliable than assumptions.

👤 User & Security Best Practices
sudo adduser devops
sudo usermod -aG sudo devops


🚫 Never use root directly in production

✔️ Use sudo for:

Audit logs

Access control

Security compliance

📄 File Permissions (Production Standard)
chmod 640 file

Entity	Access
User	Read, Write
Group	Read
Others	No Access

📌 Why:
Prevents accidental exposure of configs, keys, and logs.

📜 Logs: Your Debugging Superpower
journalctl -xe
journalctl -u nginx
journalctl -f


📌 Production Rule:

If you don’t check logs, you’re guessing.

🎯 Production-Grade Interview Questions & Answers
Q1. Why is sudo preferred over root?

Answer:
It enforces least privilege, provides audit logs, and reduces attack surface.

Q2. Difference between chmod and chown?

Answer:
chmod controls permissions, chown controls ownership. Ownership issues cause most access bugs.

Q3. How do you debug a failed service?

Answer:
Check status → inspect logs → verify config → restart service.

Q4. What happens if disk becomes 100% full?

Answer:
Applications crash, logs stop writing, SSH becomes slow or inaccessible.

Q5. How do you ensure services start after reboot?

Answer:
Use systemctl enable <service>.

🧠 DevOps Production Thinking

Always think failure first

Logs > assumptions

Permissions > code bugs

Monitoring prevents outages