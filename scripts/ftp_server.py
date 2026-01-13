from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

def main():
    # Setup anonymous authorizer
    authorizer = DummyAuthorizer()
    ftp_root = "/var/ftp"
    if not os.path.exists(ftp_root):
        os.makedirs(ftp_root, exist_ok=True)
    
    # Add anonymous user with read permissions
    authorizer.add_anonymous(ftp_root, perm='elrad')
    
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "ShadowNet FTP Server Ready"
    
    # Define passive ports for Docker compatibility
    handler.passive_ports = range(30000, 30010)
    
    # Bind to all interfaces on port 21
    address = ('0.0.0.0', 21)
    server = FTPServer(address, handler)
    
    print(f"[*] Starting Python FTP Server on {address}...")
    server.serve_forever()

if __name__ == "__main__":
    main()
