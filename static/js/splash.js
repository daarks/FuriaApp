/**
 * FURIA Know Your Fan - Splash Screen Animation
 */

document.addEventListener('DOMContentLoaded', function() {
  // Inicializa a animação da splash screen
  initSplashAnimation();
});

/**
 * Inicializa a animação da splash screen
 */
function initSplashAnimation() {
  const splashScreen = document.getElementById('splash-screen');
  const loginContainer = document.getElementById('login-form-container');
  
  if (!splashScreen || !loginContainer) {
    return;
  }
  
  // Certifica-se que o splash está visível inicialmente
  splashScreen.style.display = 'flex';
  loginContainer.style.display = 'none';
  
  // Animação de entrada do logo
  const splashLogo = document.querySelector('.splash-logo');
  if (splashLogo) {
    splashLogo.style.transform = 'scale(0.5)';
    splashLogo.style.opacity = '0';
    
    setTimeout(() => {
      splashLogo.style.transition = 'transform 1s ease, opacity 1s ease';
      splashLogo.style.transform = 'scale(1)';
      splashLogo.style.opacity = '1';
    }, 100);
  }
  
  // Após 2 segundos, inicia a animação de saída
  setTimeout(() => {
    // Animação de saída do logo
    if (splashLogo) {
      splashLogo.style.transform = 'scale(1.2)';
      splashLogo.style.opacity = '0';
    }
    
    // Após a animação do logo, remove a splash screen
    setTimeout(() => {
      splashScreen.style.opacity = '0';
      
      // Quando a splash screen desaparece, mostra o container de login
      setTimeout(() => {
        splashScreen.style.display = 'none';
        loginContainer.style.display = 'block';
        
        // Adiciona a animação de entrada no login
        setTimeout(() => {
          loginContainer.style.opacity = '1';
        }, 100);
      }, 500);
    }, 500);
  }, 2000);
}