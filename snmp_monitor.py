#!/usr/bin/env python3
"""
SNMP-based monitoring voor servers met SNMP
Vereist pysnmp: pip install pysnmp
"""
from pysnmp.hlapi import *

class SNMPMonitor:
    def __init__(self, host_ip, community='public'):
        self.host_ip = host_ip
        self.community = community
    
    def get_snmp_data(self, oid):
        """Haal SNMP data op"""
        try:
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.host_ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False):
                
                if errorIndication:
                    print(errorIndication)
                    break
                elif errorStatus:
                    print('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    break
                else:
                    for varBind in varBinds:
                        return str(varBind[1])
        except Exception as e:
            print(f"SNMP error: {e}")
        return None
    
    def get_system_info(self):
        """Haal systeem info op via SNMP"""
        data = {}
        
        # Standard SNMP OIDs
        oids = {
            'system_name': '1.3.6.1.2.1.1.5.0',          # sysName
            'system_uptime': '1.3.6.1.2.1.1.3.0',       # sysUptime
            'cpu_load': '1.3.6.1.4.1.2021.10.1.3.1',    # CPU Load (Linux)
            'memory_total': '1.3.6.1.4.1.2021.4.5.0',   # Total Memory
            'memory_used': '1.3.6.1.4.1.2021.4.6.0'     # Used Memory
        }
        
        for key, oid in oids.items():
            value = self.get_snmp_data(oid)
            if value:
                data[key] = value
        
        return data

# Voorbeeld gebruik
if __name__ == "__main__":
    monitor = SNMPMonitor('192.168.2.2')  # Ubuntu DB server
    data = monitor.get_system_info()
    print(data)