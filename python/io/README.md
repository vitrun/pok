nc -l 1234 | dd of=/dev/null

1. Use dd to give us some information about how much data was received
when the connection closes.

2. Using a distant some.remote.host will help illustrate the blocking
behaviour because data clearly can’t be transferred as quickly as the
client can copy it into the kernel.
