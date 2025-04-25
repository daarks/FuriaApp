/**
 * FURIA Know Your Fan - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash messages auto-close
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Add animation classes when elements come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 50) {
                element.classList.add('fade-in');
            }
        });
    };
    
    // Run animation check on page load and scroll
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
    
    // Form validation styling
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = document.querySelector(this.getAttribute('data-target'));
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordField.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Navigation active state based on current page
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        
        if (linkPath === currentLocation || 
            (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
    
    // Custom file input label
    const fileInputs = document.querySelectorAll('.custom-file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            let fileName = '';
            
            if (this.files && this.files.length > 1) {
                fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
            } else {
                fileName = this.value.split('\\').pop();
            }
            
            if (fileName) {
                const label = this.nextElementSibling;
                label.innerHTML = fileName;
            }
        });
    });
    
    // Fan badge tooltip
    const fanBadges = document.querySelectorAll('.fan-badge');
    
    fanBadges.forEach(badge => {
        const badgeType = badge.classList[1];
        let tooltipText = '';
        
        switch (badgeType) {
            case 'fan-badge-super':
                tooltipText = 'Super Fã: Altamente engajado em redes sociais e eventos da FURIA';
                break;
            case 'fan-badge-dedicated':
                tooltipText = 'Fã Dedicado: Regularmente acompanha a FURIA e participa ativamente';
                break;
            case 'fan-badge-regular':
                tooltipText = 'Fã Regular: Acompanha a FURIA ocasionalmente';
                break;
            case 'fan-badge-casual':
                tooltipText = 'Fã Casual: Novo na comunidade FURIA';
                break;
        }
        
        if (tooltipText) {
            badge.setAttribute('data-bs-toggle', 'tooltip');
            badge.setAttribute('data-bs-placement', 'top');
            badge.setAttribute('title', tooltipText);
        }
    });
    
    // Mobile menu close on click
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', function() {
                if (window.getComputedStyle(navbarToggler).display !== 'none') {
                    navbarToggler.click();
                }
            });
        });
    }
});
