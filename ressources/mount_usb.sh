# Stop processes
/etc/init.d/rlyeh stop
/etc/init.d/cthulhu stop
/etc/init.d/syslog-ng stop

# Unmount previous storage location
busybox umount /lcm

# Attach new storage location
busybox mount /dev/sda1 /lcm

# Check mount 
df -h

# Restart processes
/etc/init.d/syslog-ng start
/etc/init.d/cthulhu start
/etc/init.d/rlyeh start

# To keep mount on reboot
echo "mount /dev/sda1 /lcm 2>&1 >/tmp/sdb_mount" > /etc/rc.d/S89_rlyeh_preinit
chmod 777 /etc/rc.d/S89_rlyeh_preinit