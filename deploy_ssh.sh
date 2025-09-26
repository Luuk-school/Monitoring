#!/bin/bash
# SSH Key Deployment Script
# Automatisch de SSH public key naar remote servers kopiëren

echo "🔐 SSH Key Deployment naar Remote Servers"
echo "=========================================="

PUBLIC_KEY=$(cat ~/.ssh/id_rsa.pub)

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ Geen SSH public key gevonden! Voer eerst ./setup_ssh.sh uit."
    exit 1
fi

echo "📋 Public key om te installeren:"
echo "$PUBLIC_KEY"
echo ""

# Function om SSH key naar een server te kopiëren
deploy_to_server() {
    local server_ip=$1
    local server_name=$2
    local ssh_user=${3:-root}
    
    echo "🚀 Deploying key naar $server_name ($server_ip) als user '$ssh_user'..."
    
    # Probeer ssh-copy-id eerst
    if command -v ssh-copy-id >/dev/null 2>&1; then
        echo "   Proberen met ssh-copy-id..."
        if ssh-copy-id -o ConnectTimeout=10 -i ~/.ssh/id_rsa.pub "$ssh_user@$server_ip" 2>/dev/null; then
            echo "   ✅ SSH key succesvol gekopieerd met ssh-copy-id"
            return 0
        else
            echo "   ⚠️ ssh-copy-id mislukt, proberen met handmatige methode..."
        fi
    fi
    
    # Handmatige methode als fallback
    echo "   Proberen handmatige key installatie..."
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$ssh_user@$server_ip" "
        mkdir -p ~/.ssh
        echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys
        chmod 700 ~/.ssh
        chmod 600 ~/.ssh/authorized_keys
        # Remove duplicates
        sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
        mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys
        echo 'SSH key installed successfully'
    " 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "   ✅ SSH key handmatig geïnstalleerd"
        return 0
    else
        echo "   ❌ Key installatie mislukt"
        return 1
    fi
}

# Test SSH connectie
test_ssh_connection() {
    local server_ip=$1
    local server_name=$2
    local ssh_user=${3:-root}
    
    echo "🧪 Testen passwordless SSH naar $server_name ($server_ip)..."
    
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$ssh_user@$server_ip" 'echo "SSH OK: $(hostname)"' 2>/dev/null; then
        echo "   ✅ Passwordless SSH werkt!"
        return 0
    else
        echo "   ❌ Passwordless SSH werkt niet"
        return 1
    fi
}

# Deploy naar Ubuntu DB Server
echo ""
echo "=== Ubuntu Database Server ==="
deploy_to_server "192.168.2.2" "Ubuntu DB" "root"
test_ssh_connection "192.168.2.2" "Ubuntu DB" "root"

echo ""
echo "=== Ubuntu Web Server ==="
deploy_to_server "192.168.2.3" "Ubuntu Web" "root"  
test_ssh_connection "192.168.2.3" "Ubuntu Web" "root"

echo ""
echo "📊 Deployment Summary"
echo "===================="

# Test alle servers
db_status="❌"
web_status="❌"

if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@192.168.2.2 'exit' >/dev/null 2>&1; then
    db_status="✅"
fi

if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@192.168.2.3 'exit' >/dev/null 2>&1; then
    web_status="✅"
fi

echo "Ubuntu DB (192.168.2.2):  $db_status"
echo "Ubuntu Web (192.168.2.3): $web_status"

echo ""
if [[ "$db_status" == "✅" ]] && [[ "$web_status" == "✅" ]]; then
    echo "🎉 Alle SSH verbindingen werken! Je kunt nu gedetailleerde monitoring gebruiken."
    echo "   Run: python3 test_monitoring.py om te testen"
elif [[ "$db_status" == "✅" ]] || [[ "$web_status" == "✅" ]]; then
    echo "⚠️ Enkele SSH verbindingen werken. Check de servers die falen."
else
    echo "❌ Geen SSH verbindingen werken. Controleer:"
    echo "   • Zijn de servers online?"
    echo "   • Draait SSH daemon op de servers?"
    echo "   • Zijn de credentials correct?"
    echo "   • Is SSH toegang toegestaan?"
fi