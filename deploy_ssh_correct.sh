#!/bin/bash
# SSH Key Deployment Script voor de juiste gebruikers
# Ubuntu servers: ridderleeuw gebruiker
# Windows server: Luuk@bjorn.local (voor later gebruik)

echo "🔐 SSH Key Deployment naar Linux Servers"
echo "========================================"
echo "Ubuntu servers gebruiken 'ridderleeuw' als gebruiker"
echo ""

PUBLIC_KEY=$(cat ~/.ssh/id_rsa.pub)

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ Geen SSH public key gevonden! Voer eerst ./setup_ssh.sh uit."
    exit 1
fi

echo "📋 Public key om te installeren:"
echo "${PUBLIC_KEY:0:80}..."
echo ""

# Function om SSH key naar een server te kopiëren
deploy_to_server() {
    local server_ip=$1
    local server_name=$2
    local ssh_user=$3
    
    echo "🚀 Deploying key naar $server_name ($server_ip) als user '$ssh_user'..."
    
    # Probeer ssh-copy-id eerst
    if command -v ssh-copy-id >/dev/null 2>&1; then
        echo "   Proberen met ssh-copy-id..."
        if timeout 15 ssh-copy-id -o ConnectTimeout=10 -i ~/.ssh/id_rsa.pub "$ssh_user@$server_ip"; then
            echo "   ✅ SSH key succesvol gekopieerd met ssh-copy-id"
            return 0
        else
            echo "   ⚠️ ssh-copy-id mislukt, proberen met handmatige methode..."
        fi
    fi
    
    # Handmatige methode als fallback
    echo "   Proberen handmatige key installatie..."
    timeout 15 ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$ssh_user@$server_ip" "
        mkdir -p ~/.ssh
        echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys
        chmod 700 ~/.ssh
        chmod 600 ~/.ssh/authorized_keys
        # Remove duplicates
        sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
        mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys
        echo 'SSH key installed successfully'
    "
    
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
    local ssh_user=$3
    
    echo "🧪 Testen passwordless SSH naar $server_name ($server_ip) als '$ssh_user'..."
    
    if timeout 10 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$ssh_user@$server_ip" 'echo "SSH OK: $(hostname) - User: $(whoami)"'; then
        echo "   ✅ Passwordless SSH werkt!"
        return 0
    else
        echo "   ❌ Passwordless SSH werkt niet"
        return 1
    fi
}

# Deploy naar Ubuntu servers met ridderleeuw gebruiker
echo ""
echo "=== Ubuntu Database Server (als ridderleeuw) ==="
deploy_to_server "192.168.2.2" "Ubuntu DB" "ridderleeuw"
test_ssh_connection "192.168.2.2" "Ubuntu DB" "ridderleeuw"

echo ""
echo "=== Ubuntu Web Server (als ridderleeuw) ==="
deploy_to_server "192.168.2.3" "Ubuntu Web" "ridderleeuw"  
test_ssh_connection "192.168.2.3" "Ubuntu Web" "ridderleeuw"

echo ""
echo "📊 Deployment Summary"
echo "===================="

# Test alle servers met juiste gebruikersnamen
db_status="❌"
web_status="❌"

echo "Testing connections..."
if timeout 5 ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o PasswordAuthentication=no ridderleeuw@192.168.2.2 'exit' >/dev/null 2>&1; then
    db_status="✅"
fi

if timeout 5 ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o PasswordAuthentication=no ridderleeuw@192.168.2.3 'exit' >/dev/null 2>&1; then
    web_status="✅"
fi

echo ""
echo "Ubuntu DB (192.168.2.2) als ridderleeuw:  $db_status"
echo "Ubuntu Web (192.168.2.3) als ridderleeuw: $web_status"

echo ""
if [[ "$db_status" == "✅" ]] && [[ "$web_status" == "✅" ]]; then
    echo "🎉 Alle SSH verbindingen werken! Je kunt nu gedetailleerde monitoring gebruiken."
    echo ""
    echo "✨ Volgende stappen:"
    echo "   1. Run: python3 test_monitoring.py om de monitoring te testen"
    echo "   2. Run: python3 Main.py om de web interface te starten"
elif [[ "$db_status" == "✅" ]] || [[ "$web_status" == "✅" ]]; then
    echo "⚠️ Enkele SSH verbindingen werken. Check de servers die falen."
    echo "   De werkende servers krijgen gedetailleerde monitoring."
    echo "   De andere servers krijgen basic ping/port monitoring."
else
    echo "❌ Geen SSH verbindingen werken. Mogelijke oorzaken:"
    echo "   • Servers zijn offline"
    echo "   • SSH daemon draait niet"
    echo "   • Gebruiker 'ridderleeuw' bestaat niet op de servers"
    echo "   • SSH toegang is niet toegestaan voor deze gebruiker"
    echo "   • Firewall blokkeert SSH (poort 22)"
    echo ""
    echo "💡 Het systeem zal basic monitoring gebruiken (ping + port checks)"
fi

echo ""
echo "ℹ️  Windows Server Info:"
echo "   Windows Server (192.168.2.1) gebruikt basic monitoring"
echo "   Gebruiker: Luuk@bjorn.local (voor toekomstige uitbreidingen)"