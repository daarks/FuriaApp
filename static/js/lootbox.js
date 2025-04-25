/**
 * FURIA Know Your Fan - Lootbox
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize lootbox
    const lootbox = document.getElementById('lootbox');
    if (!lootbox) return;
    
    // Check if the lootbox is disabled (already opened today)
    const canOpen = lootbox.getAttribute('data-can-open') === 'true';
    
    if (canOpen) {
        // Add click event listener to open the lootbox
        lootbox.addEventListener('click', openLootbox);
    } else {
        // Lootbox is already opened today
        lootbox.classList.add('disabled');
        
        // Show countdown to next available lootbox
        showNextLootboxCountdown();
    }
    
    // Initialize tooltips for reward history items
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });
});

function openLootbox() {
    const lootbox = document.getElementById('lootbox');
    if (!lootbox || lootbox.classList.contains('opening')) return;
    
    // Set opening state to prevent multiple clicks
    lootbox.classList.add('opening');
    
    // Add opening animation
    lootbox.classList.add('opened');
    
    // Play opening sound
    playLootboxSound();
    
    // Make API call to get reward
    fetch('/open_lootbox', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to open lootbox');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Wait for animation to complete then show reward
            setTimeout(() => {
                showReward(data.reward);
                // Make lootbox disappear
                lootbox.style.display = 'none';
            }, 1000);
        } else {
            showError(data.message);
            // Reset lootbox
            lootbox.classList.remove('opened', 'opening');
        }
    })
    .catch(error => {
        console.error('Error opening lootbox:', error);
        showError('Failed to open lootbox. Please try again later.');
        // Reset lootbox
        lootbox.classList.remove('opened', 'opening');
    });
}

function showReward(reward) {
    // Create reward container if it doesn't exist
    let rewardContainer = document.getElementById('reward-container');
    if (!rewardContainer) {
        rewardContainer = document.createElement('div');
        rewardContainer.id = 'reward-container';
        rewardContainer.className = 'reward-container';
        document.querySelector('.lootbox-container').appendChild(rewardContainer);
    }
    
    // Format reward HTML
    const rewardHTML = `
        <div class="reward-image">
            <div class="reward-icon">
                ${getRewardIcon(reward.type)}
            </div>
            <span class="reward-rarity reward-rarity-${reward.rarity}">${capitalize(reward.rarity)}</span>
        </div>
        <h3 class="reward-title">${reward.name}</h3>
        <p class="reward-description">${reward.description}</p>
        ${reward.code ? `<div class="reward-code mt-3 mb-3">Código: <strong>${reward.code}</strong></div>` : ''}
        <button class="btn btn-primary mt-3 reward-close">Continuar</button>
    `;
    
    // Update container content
    rewardContainer.innerHTML = rewardHTML;
    
    // Show the container with animation
    rewardContainer.classList.add('show');
    
    // Add confetti effect
    createConfetti(reward.rarity);
    
    // Add click event for the close button
    const closeButton = rewardContainer.querySelector('.reward-close');
    closeButton.addEventListener('click', function() {
        // Hide reward container
        rewardContainer.classList.remove('show');
        
        // Refresh the page to update the lootbox state
        window.location.reload();
    });
}

function getRewardIcon(type) {
    // Return appropriate icon based on reward type
    switch (type) {
        case 'wallpaper':
            return '<i class="fas fa-image fa-3x text-furia-secondary"></i>';
        case 'avatar':
            return '<i class="fas fa-user-circle fa-3x text-furia-secondary"></i>';
        case 'gif':
            return '<i class="fas fa-film fa-3x text-furia-secondary"></i>';
        case 'discount':
            return '<i class="fas fa-percent fa-3x text-furia-secondary"></i>';
        case 'digital_item':
            return '<i class="fas fa-gift fa-3x text-furia-secondary"></i>';
        case 'exclusive':
            return '<i class="fas fa-crown fa-3x text-furia-primary"></i>';
        default:
            return '<i class="fas fa-star fa-3x text-furia-secondary"></i>';
    }
}

function createConfetti(rarity) {
    const container = document.createElement('div');
    container.className = 'confetti-container';
    document.querySelector('.lootbox-container').appendChild(container);
    
    // Set colors based on rarity
    let colors;
    let count;
    
    switch (rarity) {
        case 'legendary':
            colors = ['#FF0057', '#FF9900', '#FFFF00', '#FFFFFF', '#FFD700'];
            count = 150;
            break;
        case 'rare':
            colors = ['#00A3FF', '#00FFB7', '#FFFFFF', '#0088FF'];
            count = 100;
            break;
        case 'uncommon':
            colors = ['#00FFB7', '#FFFFFF', '#CCCCCC'];
            count = 75;
            break;
        default: // common
            colors = ['#FFFFFF', '#CCCCCC', '#AAAAAA'];
            count = 50;
    }
    
    // Create confetti pieces
    for (let i = 0; i < count; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.width = `${Math.random() * 10 + 5}px`;
        confetti.style.height = `${Math.random() * 10 + 5}px`;
        confetti.style.opacity = Math.random();
        confetti.style.animation = `confetti-fall ${Math.random() * 3 + 2}s linear forwards`;
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        
        container.appendChild(confetti);
    }
    
    // Remove container after animations
    setTimeout(() => {
        container.remove();
    }, 5000);
}

function showNextLootboxCountdown() {
    const lootboxStatus = document.getElementById('lootbox-status');
    if (!lootboxStatus) return;
    
    // Get tomorrow's date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    // Update countdown every second
    const updateCountdown = function() {
        const now = new Date();
        const diff = tomorrow - now;
        
        // Calculate hours, minutes, seconds
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        // Update status text
        lootboxStatus.textContent = `Próxima lootbox disponível em: ${hours}h ${minutes}m ${seconds}s`;
        
        // Continue countdown
        if (diff > 0) {
            setTimeout(updateCountdown, 1000);
        } else {
            // Refresh the page when the countdown ends
            window.location.reload();
        }
    };
    
    // Start countdown
    updateCountdown();
}

function playLootboxSound() {
    // Create audio element
    const audio = new Audio('/static/sounds/lootbox_open.mp3');
    
    // Try to play sound (browsers may block this if user hasn't interacted with the page)
    audio.play().catch(error => {
        console.log('Audio could not be played:', error);
    });
}

function showError(message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to page
    const alertContainer = document.getElementById('lootbox-alerts');
    if (alertContainer) {
        alertContainer.appendChild(alert);
    } else {
        // Insert before lootbox
        const lootboxContainer = document.querySelector('.lootbox-container');
        lootboxContainer.insertBefore(alert, lootboxContainer.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
