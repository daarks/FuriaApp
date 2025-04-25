/**
 * FURIA Know Your Fan - Social Media
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    const socialMediaForm = document.getElementById('social-media-form');
    if (socialMediaForm) {
        socialMediaForm.addEventListener('submit', function(event) {
            if (!validateSocialMediaForm(event)) {
                event.preventDefault();
            } else {
                // Show loading state
                showAnalysisInProgress();
            }
        });
    }
    
    // Initialize tooltips
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });
    
    // Add event listeners for social media URL validation
    const socialMediaInputs = document.querySelectorAll('.social-media-input');
    socialMediaInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateSocialMediaURL(this);
        });
        
        // Add input handler for auto-formatting
        input.addEventListener('input', function() {
            formatSocialMediaURL(this);
        });
    });
    
    // Initialize hashtag visualization if data exists
    initializeHashtagCloud();
    
    // Initialize social engagement chart if element exists
    const socialEngagementChart = document.getElementById('social-engagement-chart');
    if (socialEngagementChart && typeof initializeSocialEngagementChart === 'function') {
        try {
            const socialData = JSON.parse(socialEngagementChart.getAttribute('data-social-media') || '{}');
            if (socialData) {
                initializeSocialEngagementChart('social-engagement-chart', socialData);
            }
        } catch (e) {
            console.error('Error initializing social engagement chart:', e);
        }
    }
});

function validateSocialMediaForm(event) {
    let isValid = true;
    const form = event.target;
    
    // Check that at least one social media profile is provided
    const inputs = form.querySelectorAll('.social-media-input');
    let hasValue = false;
    
    inputs.forEach(input => {
        if (input.value.trim()) {
            hasValue = true;
            
            // Validate the URL format if provided
            if (!validateSocialMediaURL(input)) {
                isValid = false;
            }
        }
    });
    
    if (!hasValue) {
        showAlert('Por favor, forneça pelo menos um perfil de rede social.', 'warning');
        isValid = false;
    }
    
    return isValid;
}

function validateSocialMediaURL(input) {
    const value = input.value.trim();
    if (!value) return true; // Empty is allowed
    
    const name = input.name;
    let isValid = true;
    let errorMessage = '';
    
    // Basic URL validation
    if (!value.startsWith('http://') && !value.startsWith('https://')) {
        errorMessage = 'URL deve começar com http:// ou https://';
        isValid = false;
    }
    
    // Platform-specific validation
    switch (name) {
        case 'twitter':
            if (!value.includes('twitter.com') && !value.includes('x.com')) {
                errorMessage = 'URL inválida para Twitter/X';
                isValid = false;
            }
            break;
        case 'instagram':
            if (!value.includes('instagram.com')) {
                errorMessage = 'URL inválida para Instagram';
                isValid = false;
            }
            break;
        case 'twitch':
            if (!value.includes('twitch.tv')) {
                errorMessage = 'URL inválida para Twitch';
                isValid = false;
            }
            break;
        case 'youtube':
            if (!value.includes('youtube.com') && !value.includes('youtu.be')) {
                errorMessage = 'URL inválida para YouTube';
                isValid = false;
            }
            break;
        case 'facebook':
            if (!value.includes('facebook.com')) {
                errorMessage = 'URL inválida para Facebook';
                isValid = false;
            }
            break;
    }
    
    // Update UI with validation result
    const feedbackElement = input.nextElementSibling;
    if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
        feedbackElement.textContent = errorMessage;
    }
    
    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

function formatSocialMediaURL(input) {
    const value = input.value.trim();
    if (!value) return;
    
    const name = input.name;
    let formattedValue = value;
    
    // Add protocol if missing
    if (!value.startsWith('http://') && !value.startsWith('https://')) {
        formattedValue = 'https://' + value;
    }
    
    // Add platform domain if just username is entered
    switch (name) {
        case 'twitter':
            if (!formattedValue.includes('.com') && !formattedValue.includes('.tv')) {
                // Check if it's a username (starts with @ or not)
                if (formattedValue.includes('https://') && !formattedValue.includes('twitter.com') && !formattedValue.includes('x.com')) {
                    const username = formattedValue.replace('https://', '').replace('@', '');
                    formattedValue = `https://twitter.com/${username}`;
                }
            }
            break;
        case 'instagram':
            if (!formattedValue.includes('.com') && !formattedValue.includes('.tv')) {
                // Check if it's a username
                if (formattedValue.includes('https://') && !formattedValue.includes('instagram.com')) {
                    const username = formattedValue.replace('https://', '').replace('@', '');
                    formattedValue = `https://instagram.com/${username}`;
                }
            }
            break;
        case 'twitch':
            if (!formattedValue.includes('.com') && !formattedValue.includes('.tv')) {
                // Check if it's a username
                if (formattedValue.includes('https://') && !formattedValue.includes('twitch.tv')) {
                    const username = formattedValue.replace('https://', '').replace('@', '');
                    formattedValue = `https://twitch.tv/${username}`;
                }
            }
            break;
        case 'youtube':
            if (!formattedValue.includes('.com') && !formattedValue.includes('.be')) {
                // More complex, just ensure domain exists
                if (formattedValue.includes('https://') && !formattedValue.includes('youtube.com') && !formattedValue.includes('youtu.be')) {
                    const username = formattedValue.replace('https://', '');
                    formattedValue = `https://youtube.com/c/${username}`;
                }
            }
            break;
        case 'facebook':
            if (!formattedValue.includes('.com') && !formattedValue.includes('.tv')) {
                // Check if it's a username
                if (formattedValue.includes('https://') && !formattedValue.includes('facebook.com')) {
                    const username = formattedValue.replace('https://', '').replace('@', '');
                    formattedValue = `https://facebook.com/${username}`;
                }
            }
            break;
    }
    
    // Update input with formatted value if changed
    if (formattedValue !== value) {
        input.value = formattedValue;
    }
}

function showAnalysisInProgress() {
    // Hide the form
    const form = document.getElementById('social-media-form');
    if (form) {
        form.classList.add('d-none');
    }
    
    // Show loading state
    const loadingContainer = document.getElementById('analysis-loading');
    if (!loadingContainer) {
        const container = document.createElement('div');
        container.id = 'analysis-loading';
        container.className = 'text-center my-5';
        container.innerHTML = `
            <div class="spinner-border text-furia-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h4 class="mb-3">Analisando seus perfis sociais...</h4>
            <p class="text-muted">Estamos verificando suas interações e engajamento com esports e FURIA nas redes sociais.</p>
            <div class="progress mt-3">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-furia-primary" 
                     role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        `;
        
        // Add some cool loading messages that change over time
        const loadingMessages = [
            "Calculando seu nível de engajamento...",
            "Analisando hashtags utilizadas...",
            "Verificando interações com conteúdo da FURIA...",
            "Identificando padrões de participação em eventos...",
            "Processando compatibilidade com perfil de fã...",
            "Determinando seu badge de fã..."
        ];
        
        const messageElement = document.createElement('p');
        messageElement.className = 'text-furia-secondary mt-3';
        container.appendChild(messageElement);
        
        // Insert after form
        form.parentNode.insertBefore(container, form.nextSibling);
        
        // Animate progress bar
        const progressBar = container.querySelector('.progress-bar');
        let progress = 0;
        let messageIndex = 0;
        
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            
            // Update message every 20%
            if (progress % 20 === 0 && messageIndex < loadingMessages.length) {
                messageElement.textContent = loadingMessages[messageIndex];
                messageIndex++;
            }
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 300);
    }
}

function initializeHashtagCloud() {
    const hashtagsContainer = document.getElementById('hashtags-cloud');
    if (!hashtagsContainer) return;
    
    try {
        const hashtags = JSON.parse(hashtagsContainer.getAttribute('data-hashtags') || '[]');
        if (!hashtags.length) return;
        
        // Create hashtag cloud
        let html = '';
        const maxFontSize = 2.5;
        const minFontSize = 0.8;
        
        hashtags.forEach((hashtag, index) => {
            // Calculate font size based on index (first items are more important)
            const size = maxFontSize - ((index / hashtags.length) * (maxFontSize - minFontSize));
            
            // Assign random color class
            const colorClasses = ['text-furia-primary', 'text-furia-secondary', 'text-furia-accent', 'text-white'];
            const colorClass = colorClasses[index % colorClasses.length];
            
            html += `<span class="hashtag-item ${colorClass}" style="font-size: ${size}rem;">${hashtag}</span>`;
        });
        
        hashtagsContainer.innerHTML = html;
        
        // Add animation to hashtags
        const hashtagItems = document.querySelectorAll('.hashtag-item');
        hashtagItems.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('fade-in');
        });
    } catch (e) {
        console.error('Error initializing hashtag cloud:', e);
    }
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('social-media-alerts');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Clear previous alerts
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}
