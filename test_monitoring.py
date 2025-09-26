#!/usr/bin/env python3
"""
Test script voor HybridMonitoring
"""

import sys
sys.path.append('/home/ridderleeuw/Monitoring')

from hybrid_monitor import HybridMultiHostMonitor
from config import MONITORED_HOSTS

def test_all_hosts():
    """Test monitoring voor alle hosts"""
    monitor = HybridMultiHostMonitor()
    
    print("Starting hybrid monitoring test...")
    print("=" * 50)
    
    for host_id, host_info in MONITORED_HOSTS.items():
        if not host_info.get('enabled', True):
            print(f"Skipping disabled host: {host_id}")
            continue
            
        print(f"\nTesting {host_id} ({host_info['name']}):")
        print(f"  IP: {host_info['ip']}")
        print(f"  Type: {host_info.get('type', 'unknown')}")
        print(f"  Method: {host_info.get('monitoring_method', 'basic')}")
        
        try:
            data = monitor.get_host_data(host_id)
            
            if data:
                print(f"  Status: ✅ ONLINE")
                print(f"  CPU Usage: {data.get('cpu', {}).get('usage_percent', 0):.1f}%")
                print(f"  Memory Usage: {data.get('memory', {}).get('usage_percent', 0):.1f}%")
                print(f"  Disk Usage: {data.get('disk', {}).get('usage_percent', 0):.1f}%")
                print(f"  Hostname: {data.get('system', {}).get('hostname', 'unknown')}")
                print(f"  Platform: {data.get('system', {}).get('platform', 'unknown')}")
            else:
                print(f"  Status: ❌ OFFLINE")
                print(f"  Reason: No data could be retrieved")
                
        except Exception as e:
            print(f"  Status: ❌ ERROR")
            print(f"  Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_all_hosts()