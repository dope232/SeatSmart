# How to Run

1. **Clone the Repository :**
  
 ```bash
   git clone https://github.com/dope232/SeatSmart
   ```

2. **How to run the code** 
- Use the following commands to find the IP address:
  - Linux: `ip addr show`
  - Windows: `ipconfig`
  - macOS: `ifconfig`
- In both the client and server code, change the `HOST` variable to the IP address obtained when connected to the same host.
- When prompted with a passphrase, enter `dhan`.
- Run the server on one device.
-  ```bash
   python run server.py 
   ```
- Run the client on another device.
-  ```bash
   python run clientgui1.py 
   ```
- Now the clients can use the application.

