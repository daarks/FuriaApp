/**
 * FURIA Know Your Fan - Lootbox
 */

function openLootbox() {
    const lootboxElement = document.getElementById('lootbox');
    const lootboxImg = document.getElementById('lootbox-img');
    
    // Check if lootbox is disabled
    if (!lootboxElement || lootboxElement.classList.contains('disabled')) {
        return;
    }
    
    // Check if already opening
    if (lootboxElement.classList.contains('opening')) {
        return;
    }
    
    // Add opening animation
    lootboxElement.classList.add('opening');
    
    // Play sound effect if available
    playLootboxSound();
    
    // Show loading animation
    const loadingToast = showLoading('Abrindo lootbox...');
    
    // Versão offline que não depende de requisição ao servidor
    // Gerar recompensa aleatória localmente
    setTimeout(() => {
        // Remover toast de carregamento
        if (loadingToast) {
            document.body.removeChild(loadingToast);
        }
        
        // Gerar recompensa aleatória
        const reward = getRandomLocalReward();
        console.log('Lootbox opened with local reward:', reward);
        
        // Animar abertura da lootbox
        lootboxElement.classList.add('opened');
        
        // Mudar imagem da lootbox para aberta
        if (lootboxImg) {
            lootboxImg.src = '/static/img/lootbox_open.png';
            lootboxImg.style.transform = 'scale(1.2)';
            lootboxImg.style.filter = 'brightness(1.5)';
        }
        
        // Mostrar recompensa
        showReward(reward);
        
        // Desabilitar lootbox após abrir
        lootboxElement.classList.add('disabled');
        
        // Adicionar overlay indicando que foi aberta
        const overlay = document.createElement('div');
        overlay.className = 'app-lootbox-overlay';
        overlay.innerHTML = '<i class="fas fa-lock"></i>';
        lootboxElement.appendChild(overlay);
    }, 1500);
}

function showReward(reward) {
    const rewardContainer = document.getElementById('reward-container');
    if (!rewardContainer) return;
    
    // Clear container
    rewardContainer.innerHTML = '';
    
    // Create reward header
    const headerElement = document.createElement('h3');
    headerElement.textContent = 'Parabéns!';
    headerElement.className = 'app-reward-header';
    rewardContainer.appendChild(headerElement);
    
    // Create reward element
    const rewardElement = document.createElement('div');
    rewardElement.className = `app-reward-item app-reward-${reward.rarity}`;
    
    // Reward icon
    const iconElement = document.createElement('div');
    iconElement.className = 'app-reward-icon';
    iconElement.innerHTML = getRewardIcon(reward.type);
    
    // Reward info
    const infoElement = document.createElement('div');
    infoElement.className = 'app-reward-info';
    
    const nameElement = document.createElement('h3');
    nameElement.className = 'app-reward-name';
    nameElement.textContent = reward.name;
    
    const rarityElement = document.createElement('div');
    rarityElement.className = `app-reward-rarity rarity-${reward.rarity}`;
    rarityElement.textContent = capitalize(reward.rarity);
    
    const descElement = document.createElement('p');
    descElement.className = 'app-reward-desc';
    descElement.textContent = reward.description || `Um item ${reward.rarity} exclusivo FURIA!`;
    
    // Add elements to DOM
    infoElement.appendChild(nameElement);
    infoElement.appendChild(rarityElement);
    infoElement.appendChild(descElement);
    
    rewardElement.appendChild(iconElement);
    rewardElement.appendChild(infoElement);
    
    rewardContainer.appendChild(rewardElement);
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'app-btn app-btn-primary app-mt-2';
    closeButton.textContent = 'Fechar';
    closeButton.onclick = function() {
        // Hide reward container and reload page to update rewards list
        rewardContainer.classList.remove('show');
        setTimeout(() => {
            window.location.reload();
        }, 500);
    };
    rewardContainer.appendChild(closeButton);
    
    // Show container with animation
    rewardContainer.classList.add('show');
    
    // Create confetti effect for rare/legendary rewards
    if (reward.rarity === 'rare' || reward.rarity === 'legendary') {
        createConfetti(reward.rarity);
    }
}

function getRewardIcon(type) {
    const icons = {
        'wallpaper': '<i class="fas fa-image"></i>',
        'avatar': '<i class="fas fa-user-circle"></i>',
        'gif': '<i class="fas fa-film"></i>',
        'discount': '<i class="fas fa-percent"></i>',
        'digital_item': '<i class="fas fa-gift"></i>',
        'exclusive': '<i class="fas fa-crown"></i>'
    };
    
    return icons[type] || '<i class="fas fa-question"></i>';
}

function createConfetti(rarity) {
    const confettiContainer = document.querySelector('.confetti-container');
    if (!confettiContainer) return;
    
    // Colors based on rarity
    const colors = rarity === 'legendary' ? 
        ['#ff0057', '#ff4081', '#ffffff', '#ffcc00'] : 
        ['#1e90ff', '#42A5F5', '#ffffff', '#64b5f6'];
    
    // Create confetti pieces
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        
        confettiContainer.appendChild(confetti);
    }
    
    // Remove confetti after animation
    setTimeout(() => {
        confettiContainer.innerHTML = '';
    }, 5000);
}

function playLootboxSound() {
    // Create audio element if supported
    try {
        const audio = new Audio('/static/audio/lootbox_open.mp3');
        audio.volume = 0.5;
        audio.play().catch(e => console.log('Audio playback prevented:', e));
    } catch (e) {
        console.log('Audio playback not supported');
    }
}

function showLoading(message) {
    const toast = document.createElement('div');
    toast.className = 'app-toast app-toast-loading';
    toast.innerHTML = `
        <div class="app-toast-content">
            <div class="app-loading-spinner"></div>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    return toast;
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'app-toast app-toast-error';
    toast.innerHTML = `<div class="app-toast-content">${message}</div>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function capitalize(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Constantes para recompensas locais
const LOCAL_REWARDS = [
    {
        "type": "wallpaper",
        "name": "FURIA Team Wallpaper 2023",
        "rarity": "common",
        "description": "Papel de parede para desktop com a equipe FURIA CS:GO.",
        "image": "furia_team_wallpaper.jpg"
    },
    {
        "type": "wallpaper",
        "name": "FURIA Logo Pattern",
        "rarity": "common",
        "description": "Papel de parede com padrão elegante do logo da FURIA para seu desktop ou dispositivo móvel.",
        "image": "furia_pattern_wallpaper.jpg"
    },
    {
        "type": "avatar",
        "name": "FURIA Fan Avatar",
        "rarity": "common",
        "description": "Avatar de perfil mostrando seu status de fã da FURIA.",
        "image": "furia_avatar.png"
    },
    {
        "type": "gif",
        "name": "FURIA Victory Animation",
        "rarity": "uncommon",
        "description": "GIF animado celebrando uma vitória da FURIA em torneio.",
        "image": "furia_victory.gif"
    },
    {
        "type": "discount",
        "name": "10% Off FURIA Store",
        "rarity": "uncommon",
        "description": "Código de desconto de 10% para sua próxima compra na loja oficial da FURIA.",
        "code": "FURIAFAN10"
    },
    {
        "type": "wallpaper",
        "name": "KSCERATO Highlight Wallpaper",
        "rarity": "uncommon",
        "description": "Papel de parede premium com KSCERATO em ação.",
        "image": "kscerato_wallpaper.jpg"
    },
    {
        "type": "digital_item",
        "name": "FURIA Digital Sticker Pack",
        "rarity": "uncommon",
        "description": "Coleção de adesivos digitais para usar em suas redes sociais.",
        "image": "furia_stickers.png"
    },
    {
        "type": "discount",
        "name": "15% Off FURIA Store",
        "rarity": "rare",
        "description": "Código de desconto de 15% para sua próxima compra na loja oficial da FURIA.",
        "code": "SUPERFAN15"
    },
    {
        "type": "digital_item",
        "name": "Exclusive FURIA Mousepad Design",
        "rarity": "rare",
        "description": "Design digital de um mousepad de edição limitada da FURIA.",
        "image": "furia_mousepad.png"
    },
    {
        "type": "exclusive",
        "name": "FURIA Player Signed Digital Card",
        "rarity": "legendary",
        "description": "Cartão colecionável digital com uma assinatura digital de um jogador da FURIA.",
        "image": "signed_card.png"
    }
];

// Função para obter uma recompensa aleatória com base na raridade
function getRandomLocalReward() {
    // Determinar raridade com probabilidades ponderadas
    const rarityRoll = Math.random();
    let rarity;
    
    if (rarityRoll < 0.02) { // 2% chance de legendário
        rarity = "legendary";
    } else if (rarityRoll < 0.15) { // 13% chance de raro
        rarity = "rare";
    } else if (rarityRoll < 0.40) { // 25% chance de incomum
        rarity = "uncommon";
    } else { // 60% chance de comum
        rarity = "common";
    }
    
    // Filtrar recompensas pela raridade
    const possibleRewards = LOCAL_REWARDS.filter(reward => reward.rarity === rarity);
    
    // Selecionar recompensa aleatória com raridade correspondente
    if (possibleRewards.length > 0) {
        const randomIndex = Math.floor(Math.random() * possibleRewards.length);
        const reward = {...possibleRewards[randomIndex]};
        
        // Adicionar identificador único à recompensa
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let rewardId = '';
        for (let i = 0; i < 8; i++) {
            rewardId += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        
        reward.id = rewardId;
        reward.obtained_at = new Date().toISOString();
        
        return reward;
    } else {
        // Fallback para comum se nenhuma recompensa corresponder
        const commonRewards = LOCAL_REWARDS.filter(r => r.rarity === "common");
        const randomIndex = Math.floor(Math.random() * commonRewards.length);
        return {...commonRewards[randomIndex]};
    }
}