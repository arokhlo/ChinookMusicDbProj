import socket
import subprocess
import requests
import psycopg2

def test_basic_connectivity():
    print("🔍 Testing basic network connectivity to Neon...")
    
    host = "ep-long-dust-aggdj4tj.c-2.eu-central-1.aws.neon.tech"
    port = 5432
    
    # Test 1: DNS Resolution
    try:
        ip_address = socket.gethostbyname(host)
        print(f"✅ DNS Resolution: {host} -> {ip_address}")
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # Test 2: TCP Connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP Connection to {host}:{port} - SUCCESS")
        else:
            print(f"❌ TCP Connection to {host}:{port} - FAILED (Error code: {result})")
            return False
    except Exception as e:
        print(f"❌ TCP Connection test failed: {e}")
        return False
    
    # Test 3: Ping (if available)
    try:
        result = subprocess.run(
            ["ping", "-n", "4", host], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        if result.returncode == 0:
            print("✅ Ping test - SUCCESS")
        else:
            print("⚠️ Ping test - Some packets lost (may be normal for cloud services)")
    except Exception as e:
        print(f"⚠️ Ping test not available: {e}")
    
    return True

def test_neon_status():
    print("\n🔍 Checking Neon status...")
    try:
        response = requests.get("https://status.neon.tech/", timeout=10)
        if response.status_code == 200:
            print("✅ Neon status page is accessible")
        else:
            print("⚠️ Could not access Neon status page")
    except Exception as e:
        print(f"⚠️ Could not check Neon status: {e}")

def test_with_different_ssl_modes():
    print("\n🔍 Testing different SSL modes...")
    
    connection_params = {
        'host': 'ep-long-dust-aggdj4tj.c-2.eu-central-1.aws.neon.tech',
        'port': '5432',
        'database': 'neondb',
        'user': 'your_username',  # Replace with actual username
        'password': 'your_password',  # Replace with actual password
    }
    
    ssl_modes = ['require', 'prefer', 'disable']
    
    for ssl_mode in ssl_modes:
        try:
            params = connection_params.copy()
            params['sslmode'] = ssl_mode
            conn = psycopg2.connect(**params)
            print(f"✅ SSL mode '{ssl_mode}' - SUCCESS")
            conn.close()
            return True
        except Exception as e:
            print(f"❌ SSL mode '{ssl_mode}' - FAILED: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive network diagnostics...\n")
    
    # Test basic connectivity
    if test_basic_connectivity():
        print("\n🌐 Basic network connectivity: OK")
    else:
        print("\n🌐 Basic network connectivity: FAILED")
        print("\n💡 Immediate solutions:")
        print("1. Check your internet connection")
        print("2. Try using a different network (mobile hotspot)")
        print("3. Contact your network administrator about firewall restrictions")
    
    # Check Neon status
    test_neon_status()
    
    # Test different SSL modes
    print("\n🔄 Testing connection with different SSL modes...")
    test_with_different_ssl_modes()