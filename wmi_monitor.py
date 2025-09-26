#!/usr/bin/env python3
"""
WMI-based monitoring for Windows servers
Vereist impacket: pip install impacket
"""
from impacket.dcerpc.v5.dcomrt import DCOMConnection
from impacket.dcerpc.v5.dcom import wmi
import sys

class WMIMonitor:
    def __init__(self, host_ip, username, password, domain=''):
        self.host_ip = host_ip
        self.username = username
        self.password = password
        self.domain = domain
        self.dcom = None
        self.wmi_connection = None
    
    def connect(self):
        """Maak WMI verbinding"""
        try:
            self.dcom = DCOMConnection(self.host_ip, self.username, self.password, self.domain)
            iInterface = self.dcom.CoCreateInstanceEx(wmi.CLSID_WbemLevel1Login, wmi.IID_IWbemLevel1Login)
            iWbemLevel1Login = wmi.IWbemLevel1Login(iInterface)
            self.wmi_connection = iWbemLevel1Login.NTLMLogin('//./root/cimv2', None, None)
            return True
        except Exception as e:
            print(f"WMI connection failed: {e}")
            return False
    
    def get_system_info(self):
        """Haal Windows systeem info op via WMI"""
        if not self.connect():
            return None
            
        try:
            data = {}
            
            # CPU informatie
            cpu_query = "SELECT LoadPercentage FROM Win32_Processor"
            cpu_result = self.wmi_connection.ExecQuery(cpu_query)
            if cpu_result:
                data['cpu_usage'] = cpu_result[0]['LoadPercentage']
            
            # Memory informatie  
            mem_query = "SELECT TotalVisibleMemorySize, FreePhysicalMemory FROM Win32_OperatingSystem"
            mem_result = self.wmi_connection.ExecQuery(mem_query)
            if mem_result:
                total_mem = int(mem_result[0]['TotalVisibleMemorySize'])
                free_mem = int(mem_result[0]['FreePhysicalMemory'])
                used_mem = total_mem - free_mem
                data['memory_usage'] = (used_mem / total_mem) * 100
            
            # Disk informatie
            disk_query = "SELECT Size, FreeSpace FROM Win32_LogicalDisk WHERE DriveType=3"
            disk_result = self.wmi_connection.ExecQuery(disk_query)
            if disk_result:
                total_disk = sum(int(disk['Size']) for disk in disk_result)
                free_disk = sum(int(disk['FreeSpace']) for disk in disk_result)
                used_disk = total_disk - free_disk
                data['disk_usage'] = (used_disk / total_disk) * 100
            
            data['status'] = 'online'
            return data
            
        except Exception as e:
            print(f"WMI query failed: {e}")
            return None
        finally:
            if self.dcom:
                self.dcom.disconnect()

# Voorbeeld configuratie voor Windows AD server
if __name__ == "__main__":
    monitor = WMIMonitor('192.168.2.1', 'Administrator', 'your_password')
    data = monitor.get_system_info()
    print(data)