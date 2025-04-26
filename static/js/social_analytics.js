/**
 * FURIA Know Your Fan - Social Media Analytics
 */

// Função para analisar dados de redes sociais
function analyzeSocialMedia() {
  // Apenas analisamos se temos pelo menos uma rede social conectada
  const socialInputs = document.querySelectorAll('.social-media-input');
  let hasValidSocial = false;
  
  socialInputs.forEach(input => {
    if (input.value && input.value.trim() !== '') {
      hasValidSocial = true;
    }
  });
  
  if (!hasValidSocial) {
    showMessage('Por favor, adicione pelo menos uma rede social para análise.', 'warning');
    return;
  }
  
  // Mostrar animação de carregamento
  const analyzeBtn = document.getElementById('analyze-btn');
  const originalText = analyzeBtn.textContent;
  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analisando...';
  
  // Coletar dados dos inputs de redes sociais
  const socialData = {};
  socialInputs.forEach(input => {
    if (input.value && input.value.trim() !== '') {
      socialData[input.id] = input.value;
    }
  });
  
  // Enviar dados para o servidor para análise
  fetch('/social_media', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify(socialData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Resposta da rede não foi ok');
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      // Atualizar UI com os resultados da análise
      updateSocialAnalyticsUI(data.analytics);
      showMessage('Análise social concluída com sucesso!', 'success');
      
      // Se fornecido, atualizar badge de fã
      if (data.fan_badge) {
        document.getElementById('fan-badge').textContent = data.fan_badge;
        // Destacar visualmente o novo badge
        highlightFanBadge();
      }
    } else {
      showMessage(data.message || 'Erro na análise. Tente novamente.', 'error');
    }
  })
  .catch(error => {
    console.error('Erro na análise social:', error);
    showMessage('Falha ao comunicar com o servidor. Verifique suas redes sociais ou tente novamente mais tarde.', 'error');
  })
  .finally(() => {
    // Restaurar botão
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = originalText;
  });
}

// Função para atualizar UI com os resultados da análise
function updateSocialAnalyticsUI(analytics) {
  // Pontuação de engajamento
  if (analytics.engagement_score) {
    const scoreElement = document.getElementById('engagement-score');
    if (scoreElement) {
      // Animar a pontuação
      animateCounter(scoreElement, 0, Math.round(analytics.engagement_score));
      
      // Atualizar barra de progresso
      const progressBar = document.querySelector('.engagement-progress-bar');
      if (progressBar) {
        progressBar.style.width = `${analytics.engagement_score}%`;
      }
    }
  }
  
  // Hashtags populares
  if (analytics.hashtags && analytics.hashtags.length > 0) {
    const hashtagsContainer = document.getElementById('popular-hashtags');
    if (hashtagsContainer) {
      hashtagsContainer.innerHTML = '';
      analytics.hashtags.forEach(hashtag => {
        const tag = document.createElement('span');
        tag.className = 'app-badge app-hashtag';
        tag.textContent = `#${hashtag}`;
        hashtagsContainer.appendChild(tag);
      });
    }
  }
  
  // Interações com marcas
  if (analytics.brand_interactions && analytics.brand_interactions.length > 0) {
    const brandsContainer = document.getElementById('brand-interactions');
    if (brandsContainer) {
      brandsContainer.innerHTML = '';
      analytics.brand_interactions.forEach(brand => {
        const brandElement = document.createElement('div');
        brandElement.className = 'brand-interaction-item';
        
        const brandLogo = document.createElement('div');
        brandLogo.className = 'brand-logo';
        // Adicionar logo ou ícone da marca aqui (pode ser substituído por um ícone genérico)
        brandLogo.innerHTML = `<i class="fas fa-building"></i>`;
        
        const brandInfo = document.createElement('div');
        brandInfo.className = 'brand-info';
        brandInfo.innerHTML = `
          <div class="brand-name">${brand.name}</div>
          <div class="brand-stats">
            <span><i class="fas fa-heart"></i> ${brand.likes || 0}</span>
            <span><i class="fas fa-comment"></i> ${brand.comments || 0}</span>
            <span><i class="fas fa-share"></i> ${brand.shares || 0}</span>
          </div>
        `;
        
        brandElement.appendChild(brandLogo);
        brandElement.appendChild(brandInfo);
        brandsContainer.appendChild(brandElement);
      });
    }
  }
  
  // Mostrar o container de resultados
  const resultsContainer = document.getElementById('analytics-results');
  if (resultsContainer) {
    resultsContainer.style.display = 'block';
  }
}

// Função para animar contador
function animateCounter(element, start, end, duration = 1000) {
  let startTime = null;
  
  function animation(currentTime) {
    if (!startTime) startTime = currentTime;
    const progress = Math.min((currentTime - startTime) / duration, 1);
    const value = Math.floor(progress * (end - start) + start);
    element.textContent = value;
    
    if (progress < 1) {
      window.requestAnimationFrame(animation);
    } else {
      element.textContent = end;
    }
  }
  
  window.requestAnimationFrame(animation);
}

// Função para destacar visualmente uma mudança no badge de fã
function highlightFanBadge() {
  const badge = document.getElementById('fan-badge');
  if (!badge) return;
  
  badge.classList.add('badge-highlight');
  setTimeout(() => {
    badge.classList.remove('badge-highlight');
  }, 3000);
}

// Função para mostrar mensagem na UI
function showMessage(message, type = 'info') {
  // Verificar se existe um sistema de toast ou alerta na aplicação
  if (typeof showToast === 'function') {
    showToast(message, type);
  } else {
    // Fallback para alert simples
    alert(message);
  }
}

// Função auxiliar para obter token CSRF para requisições POST
function getCsrfToken() {
  // Buscar o token de uma meta tag ou de um input hidden
  const tokenElement = document.querySelector('meta[name="csrf-token"]') || 
                      document.querySelector('input[name="csrf_token"]');
  
  return tokenElement ? tokenElement.content || tokenElement.value : '';
}

// Escutar eventos de click no botão de análise
document.addEventListener('DOMContentLoaded', function() {
  const analyzeBtn = document.getElementById('analyze-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      analyzeSocialMedia();
    });
  }
  
  // Inicializar tooltips e outros elementos de UI se necessário
  initializeUiElements();
});

// Inicializar elementos da UI
function initializeUiElements() {
  // Mostrar tooltips para explicar como funciona a pontuação
  const tooltips = document.querySelectorAll('.app-tooltip');
  tooltips.forEach(tooltip => {
    tooltip.addEventListener('mouseenter', function() {
      const content = this.getAttribute('data-tooltip');
      if (!content) return;
      
      const tooltipElement = document.createElement('div');
      tooltipElement.className = 'app-tooltip-content';
      tooltipElement.textContent = content;
      
      this.appendChild(tooltipElement);
    });
    
    tooltip.addEventListener('mouseleave', function() {
      const tooltipContent = this.querySelector('.app-tooltip-content');
      if (tooltipContent) {
        tooltipContent.remove();
      }
    });
  });
}