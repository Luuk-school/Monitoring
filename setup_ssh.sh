#!/bin/bash
# SSH Key Setup Script voor Monitoring
# Dit script helpt met het instellen van SSH keys voor passwordless monitoring

echo "🔑 SSH Key Setup voor Multi-Host Monitoring"
echo "=========================================="

# Check of SSH key al bestaat
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "📝 Genereren van nieuwe SSH key..."
    ssh-keygen -t rsa -b 4096 -C "monitoring@$(hostname)" -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH key gegenereerd: ~/.ssh/id_rsa"
else
    echo "✅ SSH key bestaat al: ~/.ssh/id_rsa"
fi

echo ""
echo "🔐 Public key (voeg deze toe aan authorized_keys op remote servers):"
echo "================================================================="
cat ~/.ssh/id_rsa.pub
echo ""

echo "📋 Setup instructies voor remote Linux servers:"
echo "=============================================="
echo "Voor elke Linux server (ubuntu-db, ubuntu-web):"
echo "1. Log in op de server als root of sudo user"
echo "2. Voer dit commando uit:"
echo ""
echo "   mkdir -p ~/.ssh && echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
echo ""
echo "3. Test de verbinding met:"
echo "   ssh root@192.168.2.2 'hostname'"
echo "   ssh root@192.168.2.3 'hostname'"
echo ""

echo "🧪 Wil je de SSH verbindingen nu testen? (y/n)"
read -r test_ssh

if [ "$test_ssh" = "y" ]; then
    echo ""
    echo "🔍 Testen SSH verbindingen..."
    
    # Test Ubuntu DB server
    echo -n "Testing ubuntu-db (192.168.2.2): "
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@192.168.2.2 'echo "connected"' >/dev/null 2>&1; then
        echo "✅ SUCCESS"
    else
        echo "❌ FAILED"
        echo "   Zorg ervoor dat de public key is toegevoegd aan ~/.ssh/authorized_keys"
    fi
    
    # Test Ubuntu Web server  
    echo -n "Testing ubuntu-web (192.168.2.3): "
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@192.168.2.3 'echo "connected"' >/dev/null 2>&1; then
        echo "✅ SUCCESS"
    else
        echo "❌ FAILED"
        echo "   Zorg ervoor dat de public key is toegevoegd aan ~/.ssh/authorized_keys"
    fi
fi

echo ""
echo "📊 Monitoring configuratie:"
echo "=========================="
echo "Na het instellen van SSH keys, zal het monitoring systeem:"
echo "• Windows server (192.168.2.1): Basic ping + port checks"
echo "• Linux servers (192.168.2.2, 192.168.2.3): Gedetailleerde SSH monitoring"
echo "• Localhost (192.168.2.5): Volledige lokale monitoring"
echo ""
echo "🚀 Start je monitoring applicatie met: python3 Main.py"