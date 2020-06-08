# /usr/bin/env sh

# Magic thing: https://github.com/NixOS/nixpkgs/issues/18358
chown root:root /var/empty

/usr/sbin/sshd -D
