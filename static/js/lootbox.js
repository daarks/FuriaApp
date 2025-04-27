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
    
    // Add opening animation
    lootboxElement.classList.add('opening');
    
    // Play sound effect if available
    playLootboxSound();
    
    // Send request to server
    fetch('/open_lootbox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            setTimeout(() => {
                lootboxElement.classList.add('opened');
                // Change lootbox image to open
                if (lootboxImg) {
                    lootboxImg.src = '/static/img/lootbox_closed.png';
                    lootboxImg.style.transform = 'scale(1.2)';
                    lootboxImg.style.filter = 'brightness(1.5)';
                }
                showReward(data.reward);
            }, 1000);
        } else {
            showError(data.message || 'Erro ao abrir lootbox');
            lootboxElement.classList.remove('opening');
        }
    })
    .catch(error => {
        console.error('Error opening lootbox:', error);
        showError('Erro ao comunicar com o servidor. Tente novamente.');
        lootboxElement.classList.remove('opening');
    });
}

function showReward(reward) {
    const rewardContainer = document.getElementById('reward-container');
    if (!rewardContainer) return;
    
    // Clear container
    rewardContainer.innerHTML = '';
    
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
    
    // Add elements to DOM
    infoElement.appendChild(nameElement);
    infoElement.appendChild(rarityElement);
    
    rewardElement.appendChild(iconElement);
    rewardElement.appendChild(infoElement);
    
    rewardContainer.appendChild(rewardElement);
    
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