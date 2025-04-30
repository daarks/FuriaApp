/**
 * FURIA Know Your Fan - App Version
 * Main application JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar a aplicação
  initializeApp();
});

/**
 * Inicializa a aplicação
 */
function initializeApp() {
  // Splash screen e animação
  const splashScreen = document.getElementById('splash-screen');
  if (splashScreen) {
    setTimeout(function() {
      splashScreen.classList.add('fade-out');
      setTimeout(function() {
        splashScreen.style.display = 'none';
        document.getElementById('login-form-container').classList.add('fade-in');
      }, 500);
    }, 2000); // Mostra a splash por 2 segundos
  }
  
  // Inicializar navegação do footer
  initializeFooterNavigation();
  
  // Inicializar outras funcionalidades
  initializeFormValidation();
  initializeNotifications();
  initializeCheckboxes();
}

/**
 * Inicializa a navegação do footer
 */
function initializeFooterNavigation() {
  const footerItems = document.querySelectorAll('.footer-nav-item');
  
  footerItems.forEach(item => {
    item.addEventListener('click', function(e) {
      // Se o item já estiver ativo, não faz nada
      if (this.classList.contains('active')) {
        return;
      }
      
      // Remove active de todos os itens
      footerItems.forEach(navItem => navItem.classList.remove('active'));
      
      // Adiciona active ao item clicado
      this.classList.add('active');
      
      // Solicita a página correspondente via AJAX se necessário
      // Implementação depende da estrutura da aplicação
    });
  });
}

/**
 * Inicializa validação de formulários
 */
function initializeFormValidation() {
  const forms = document.querySelectorAll('.app-form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        showValidationErrors(form);
      }
      
      form.classList.add('was-validated');
    });
  });
}

/**
 * Mostra erros de validação em um formulário
 */
function showValidationErrors(form) {
  const invalidFields = form.querySelectorAll(':invalid');
  
  invalidFields.forEach(field => {
    const feedbackElement = field.nextElementSibling;
    if (feedbackElement && feedbackElement.classList.contains('app-form-feedback')) {
      feedbackElement.style.display = 'block';
    }
  });
}

/**
 * Inicializa sistema de notificações
 */
function initializeNotifications() {
  // Fecha alertas ao clicar no botão de fechar
  const closeButtons = document.querySelectorAll('.app-alert .close');
  
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const alert = this.closest('.app-alert');
      alert.classList.add('fade-out');
      setTimeout(() => alert.remove(), 300);
    });
  });
}

/**
 * Inicializa as checkboxes para garantir funcionalidade de múltipla seleção
 */
function initializeCheckboxes() {
  // Busca todas as checkboxes na página
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  
  checkboxes.forEach(checkbox => {
    // Adiciona evento para quando o usuário clicar no item inteiro (não apenas na checkbox)
    const parent = checkbox.closest('.app-checkbox-item');
    if (parent) {
      parent.addEventListener('click', function(e) {
        // Impede propagação se o clique foi diretamente na checkbox
        if (e.target !== checkbox) {
          e.preventDefault();
          // Toggle o estado da checkbox
          checkbox.checked = !checkbox.checked;
          // Atualiza a classe do elemento pai
          this.classList.toggle('checked', checkbox.checked);
          // Dispara o evento de mudança para que qualquer listener na checkbox seja notificado
          checkbox.dispatchEvent(new Event('change'));
        }
      });
      
      // Adiciona também evento na própria checkbox para garantir
      checkbox.addEventListener('change', function() {
        // Atualiza o elemento pai com a classe correta
        parent.classList.toggle('checked', this.checked);
        
        console.log(`Checkbox ${this.id} alterada para: ${this.checked}`);
      });
      
      // Inicializa a aparência visual baseada no estado atual
      parent.classList.toggle('checked', checkbox.checked);
    }
  });
}

/**
 * Funções utilitárias
 */

// Mostra uma notificação temporária
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `app-toast app-toast-${type}`;
  toast.textContent = message;
  
  const container = document.getElementById('toast-container');
  if (!container) {
    const newContainer = document.createElement('div');
    newContainer.id = 'toast-container';
    document.body.appendChild(newContainer);
    newContainer.appendChild(toast);
  } else {
    container.appendChild(toast);
  }
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Carrega conteúdo para uma div via AJAX
function loadContent(url, targetElement, callback) {
  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(html => {
      document.getElementById(targetElement).innerHTML = html;
      if (callback && typeof callback === 'function') {
        callback();
      }
    })
    .catch(error => {
      console.error('Error loading content:', error);
      showToast('Erro ao carregar conteúdo. Tente novamente.', 'error');
    });
}

// Funções para autenticação com redes sociais
function connectSocialMedia(platform) {
  // URLs para as APIs de autenticação das plataformas
  const authUrls = {
    twitter: '/auth/twitter',
    instagram: '/auth/instagram',
    twitch: '/auth/twitch',
    youtube: '/auth/youtube',
    facebook: '/auth/facebook'
  };
  
  // Verifica se a plataforma é suportada
  if (!authUrls[platform]) {
    showToast('Plataforma não suportada', 'error');
    return;
  }
  
  // Abre uma janela popup para autenticação OAuth
  const width = 600;
  const height = 600;
  const left = (screen.width - width) / 2;
  const top = (screen.height - height) / 2;
  
  window.open(
    authUrls[platform],
    `Conectar ${platform}`,
    `width=${width},height=${height},left=${left},top=${top}`
  );
}

// Handler para receber o callback de autenticação
window.handleSocialAuthCallback = function(platform, success, data) {
  if (success) {
    showToast(`Conectado com ${platform} com sucesso!`, 'success');
    updateSocialConnectStatus(platform, true);
  } else {
    showToast(`Falha ao conectar com ${platform}`, 'error');
  }
};

// Atualiza o status de conexão de uma rede social na UI
function updateSocialConnectStatus(platform, isConnected) {
  const statusElement = document.querySelector(`.social-connect-${platform} .social-connect-status`);
  if (statusElement) {
    statusElement.textContent = isConnected ? 'Conectado' : 'Não conectado';
    statusElement.classList.toggle('connected', isConnected);
  }
  
  const buttonElement = document.querySelector(`.social-connect-${platform} .app-btn`);
  if (buttonElement) {
    buttonElement.textContent = isConnected ? 'Desconectar' : 'Conectar';
    buttonElement.classList.toggle('app-btn-outline', !isConnected);
  }
}

// Função para manipular o lootbox
function openLootbox() {
  const lootboxElement = document.getElementById('lootbox');
  if (!lootboxElement || lootboxElement.classList.contains('disabled')) {
    return;
  }
  
  // Adiciona animação de abertura
  lootboxElement.classList.add('opening');
  
  // Faz requisição para o servidor para obter a recompensa
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
        showReward(data.reward);
      }, 1000);
    } else {
      showToast(data.message, 'error');
      lootboxElement.classList.remove('opening');
    }
  })
  .catch(error => {
    console.error('Error opening lootbox:', error);
    showToast('Erro ao abrir lootbox. Tente novamente.', 'error');
    lootboxElement.classList.remove('opening');
  });
}

// Função para mostrar a recompensa do lootbox
function showReward(reward) {
  const rewardContainer = document.getElementById('reward-container');
  if (!rewardContainer) return;
  
  // Limpa o container
  rewardContainer.innerHTML = '';
  
  // Cria elementos da recompensa
  const rewardElement = document.createElement('div');
  rewardElement.className = `reward-item reward-${reward.rarity}`;
  
  // Ícone baseado no tipo
  const iconElement = document.createElement('div');
  iconElement.className = 'reward-icon';
  iconElement.innerHTML = getRewardIcon(reward.type);
  
  // Informações da recompensa
  const infoElement = document.createElement('div');
  infoElement.className = 'reward-info';
  
  const nameElement = document.createElement('h3');
  nameElement.className = 'reward-name';
  nameElement.textContent = reward.name;
  
  const rarityElement = document.createElement('div');
  rarityElement.className = `reward-rarity rarity-${reward.rarity}`;
  rarityElement.textContent = reward.rarity.charAt(0).toUpperCase() + reward.rarity.slice(1);
  
  // Adiciona elementos ao DOM
  infoElement.appendChild(nameElement);
  infoElement.appendChild(rarityElement);
  
  rewardElement.appendChild(iconElement);
  rewardElement.appendChild(infoElement);
  
  rewardContainer.appendChild(rewardElement);
  
  // Mostra o container de recompensa com animação
  rewardContainer.classList.add('show');
  
  // Adiciona confetes para recompensas raras e lendárias
  if (reward.rarity === 'rare' || reward.rarity === 'legendary') {
    createConfetti();
  }
}

// Retorna o HTML do ícone de acordo com o tipo de recompensa
function getRewardIcon(type) {
  const icons = {
    wallpaper: '<i class="fas fa-image"></i>',
    avatar: '<i class="fas fa-user-circle"></i>',
    gif: '<i class="fas fa-film"></i>',
    discount: '<i class="fas fa-percent"></i>',
    digital_item: '<i class="fas fa-gift"></i>',
    exclusive: '<i class="fas fa-crown"></i>'
  };
  
  return icons[type] || '<i class="fas fa-question"></i>';
}

// Cria efeito de confetes para recompensas especiais
function createConfetti() {
  const confettiContainer = document.querySelector('.confetti-container');
  if (!confettiContainer) return;
  
  for (let i = 0; i < 50; i++) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.left = `${Math.random() * 100}%`;
    confetti.style.animationDelay = `${Math.random() * 2}s`;
    confetti.style.backgroundColor = getRandomColor();
    
    confettiContainer.appendChild(confetti);
  }
  
  // Remove confetes após a animação
  setTimeout(() => {
    confettiContainer.innerHTML = '';
  }, 5000);
}

// Gera uma cor aleatória para confetes
function getRandomColor() {
  const colors = ['#ff0057', '#1e90ff', '#66BB6A', '#FFA726', '#EF5350', '#42A5F5', '#ffffff'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// Inicializa o quiz
function initializeQuiz() {
  const quizOptions = document.querySelectorAll('.quiz-option');
  const submitButton = document.getElementById('quiz-submit');
  
  quizOptions.forEach(option => {
    option.addEventListener('click', function() {
      // Remove a seleção de outras opções na mesma questão
      const questionId = this.dataset.question;
      document.querySelectorAll(`.quiz-option[data-question="${questionId}"]`)
        .forEach(opt => opt.classList.remove('selected'));
      
      // Seleciona esta opção
      this.classList.add('selected');
      
      // Atualiza o input hidden
      const radioInput = this.querySelector('input[type="radio"]');
      if (radioInput) {
        radioInput.checked = true;
      }
      
      // Atualiza o progresso
      updateQuizProgress();
    });
  });
  
  // Função para atualizar o progresso do quiz
  function updateQuizProgress() {
    const totalQuestions = document.querySelectorAll('.quiz-question').length;
    const answeredQuestions = document.querySelectorAll('.quiz-option.selected').length;
    
    const progressText = document.getElementById('quiz-progress-text');
    const progressBar = document.querySelector('.quiz-progress-fill');
    
    if (progressText) {
      progressText.textContent = `${answeredQuestions} de ${totalQuestions} perguntas respondidas`;
    }
    
    if (progressBar) {
      progressBar.style.width = `${(answeredQuestions / totalQuestions) * 100}%`;
    }
    
    if (submitButton) {
      submitButton.disabled = (answeredQuestions < totalQuestions);
    }
  }
}

// Busca de dados de partidas e torneios de esports
// Exemplos de APIs que podem ser utilizadas:
// - PandaScore: https://pandascore.co/
// - HLTV API: https://github.com/gigobyte/HLTV
// - Esports API: https://rapidapi.com/api-sports/api/api-esports
// - Rib.gg: https://rib.gg/api

// Função para buscar dados de torneios
function fetchTournaments() {
  showLoading('tournaments-container');
  
  fetch('/api/tournaments')
    .then(response => response.json())
    .then(data => {
      displayTournaments(data);
    })
    .catch(error => {
      console.error('Error fetching tournaments:', error);
      showErrorMessage('tournaments-container', 'Não foi possível carregar os torneios.');
    });
}

// Função para buscar dados de partidas
function fetchMatches() {
  showLoading('matches-container');
  
  fetch('/api/matches')
    .then(response => response.json())
    .then(data => {
      displayMatches(data);
    })
    .catch(error => {
      console.error('Error fetching matches:', error);
      showErrorMessage('matches-container', 'Não foi possível carregar as partidas.');
    });
}

// Mostrar indicador de carregamento
function showLoading(containerId) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
      <div class="app-loading">
        <div class="app-loading-spinner"></div>
        <p>Carregando...</p>
      </div>
    `;
  }
}

// Mostrar mensagem de erro
function showErrorMessage(containerId, message) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = `
      <div class="app-error">
        <i class="fas fa-exclamation-circle"></i>
        <p>${message}</p>
        <button class="app-btn app-btn-outline app-mt-1" onclick="retryFetch('${containerId}')">
          Tentar novamente
        </button>
      </div>
    `;
  }
}

// Função para tentar buscar dados novamente
function retryFetch(containerId) {
  if (containerId === 'tournaments-container') {
    fetchTournaments();
  } else if (containerId === 'matches-container') {
    fetchMatches();
  }
}