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
    
    // Simula abertura da lootbox - implementação local sem depender do servidor
    setTimeout(() => {
        // Remover loading após um curto período
        if (loadingToast) {
            document.body.removeChild(loadingToast);
        }
        
        // Gerar recompensa local
        const reward = generateLocalReward();
        console.log('Lootbox opened locally:', reward);
        
        // Mostrar a animação e resultado
        setTimeout(() => {
            lootboxElement.classList.add('opened');
            // Change lootbox image to open
            if (lootboxImg) {
                lootboxImg.src = '/static/img/lootbox_open.png';
                lootboxImg.style.transform = 'scale(1.2)';
                lootboxImg.style.filter = 'brightness(1.5)';
            }
            showReward(reward);
            
            // Disable lootbox after opening
            lootboxElement.classList.add('disabled');
            
            // Add overlay to indicate it's been opened
            const overlay = document.createElement('div');
            overlay.className = 'app-lootbox-overlay';
            overlay.innerHTML = '<i class="fas fa-lock"></i>';
            lootboxElement.appendChild(overlay);
            
            // Enviar a recompensa para o servidor em background
            // sem bloquear a experiência do usuário
            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                fetch('/open_lootbox', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ reward: reward }) // Enviar a recompensa já gerada
                }).catch(e => console.log('Background lootbox sync failed, will try next time'));
            } catch (e) {
                console.log('Error saving lootbox reward:', e);
            }
        }, 1000);
    }, 800);
}

// Função para gerar recompensa localmente
function generateLocalReward() {
    // Lista de possíveis recompensas
    const rewards = [
        {
            "type": "wallpaper",
            "name": "FURIA Team Wallpaper 2023",
            "rarity": "common",
            "description": "Desktop wallpaper featuring the FURIA CS:GO team.",
            "image": "furia_team_wallpaper.jpg"
        },
        {
            "type": "avatar",
            "name": "FURIA Fan Avatar",
            "rarity": "common",
            "description": "Profile avatar showing your FURIA fan status.",
            "image": "furia_avatar.png"
        },
        {
            "type": "gif",
            "name": "FURIA Victory Animation",
            "rarity": "uncommon",
            "description": "Animated GIF celebrating a FURIA tournament victory.",
            "image": "furia_victory.gif"
        },
        {
            "type": "discount",
            "name": "10% Off FURIA Store",
            "rarity": "uncommon",
            "description": "10% discount code for your next purchase at the official FURIA store.",
            "code": "FURIAFAN10"
        },
        {
            "type": "digital_item",
            "name": "FURIA Digital Sticker Pack",
            "rarity": "uncommon",
            "description": "Collection of digital stickers to use on social media.",
            "image": "furia_stickers.png"
        },
        {
            "type": "discount",
            "name": "15% Off FURIA Store",
            "rarity": "rare",
            "description": "15% discount code for your next purchase at the official FURIA store.",
            "code": "SUPERFAN15"
        },
        {
            "type": "exclusive",
            "name": "FURIA Player Signed Digital Card",
            "rarity": "legendary",
            "description": "Digital collector card featuring a digital signature from a FURIA player.",
            "image": "signed_card.png"
        }
    ];
    
    // Gerar um número aleatório para determinar a raridade
    const rarityRoll = Math.random();
    let rarityGroup = [];
    
    if (rarityRoll < 0.02) { // 2% chance
        rarityGroup = rewards.filter(r => r.rarity === 'legendary');
    } else if (rarityRoll < 0.15) { // 13% chance
        rarityGroup = rewards.filter(r => r.rarity === 'rare');
    } else if (rarityRoll < 0.40) { // 25% chance
        rarityGroup = rewards.filter(r => r.rarity === 'uncommon');
    } else { // 60% chance
        rarityGroup = rewards.filter(r => r.rarity === 'common');
    }
    
    // Se não houver recompensas na categoria desejada, volta para comum
    if (rarityGroup.length === 0) {
        rarityGroup = rewards.filter(r => r.rarity === 'common');
    }
    
    // Selecionar recompensa aleatória do grupo
    const reward = rarityGroup[Math.floor(Math.random() * rarityGroup.length)];
    
    // Adicionar ID único e data
    reward.id = generateRandomId(8);
    reward.obtained_at = new Date().toISOString();
    
    return reward;
}

// Função para gerar ID aleatório
function generateRandomId(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
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
    return string.charAt(0).toUpperCase() + string.slice(1);
}