/**
 * FURIA Know Your Fan - Quiz
 */

document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quiz-form');
    if (!quizForm) return;
    
    // Initialize quiz
    initializeQuiz();
    
    // Add event listeners for option selection
    const quizOptions = document.querySelectorAll('.quiz-option');
    quizOptions.forEach(option => {
        option.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question');
            const optionValue = this.getAttribute('data-value');
            
            // Update the hidden radio button
            const radioInput = document.querySelector(`input[name="${questionId}"][value="${optionValue}"]`);
            if (radioInput) {
                radioInput.checked = true;
            }
            
            // Update visual selection
            const options = document.querySelectorAll(`.quiz-option[data-question="${questionId}"]`);
            options.forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            
            // Update progress
            updateQuizProgress();
        });
    });
    
    // Add event listener for form submission
    quizForm.addEventListener('submit', function(event) {
        // Check if all questions are answered
        const unansweredQuestions = document.querySelectorAll('.quiz-question:not(.answered)');
        
        if (unansweredQuestions.length > 0) {
            event.preventDefault();
            
            // Show alert
            const alertElement = document.createElement('div');
            alertElement.className = 'alert alert-danger alert-dismissible fade show mt-3';
            alertElement.innerHTML = `
                Por favor, responda todas as ${unansweredQuestions.length} perguntas restantes.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            const alertContainer = document.getElementById('quiz-alerts');
            if (alertContainer) {
                // Clear previous alerts
                alertContainer.innerHTML = '';
                alertContainer.appendChild(alertElement);
            } else {
                quizForm.insertBefore(alertElement, quizForm.firstChild);
            }
            
            // Scroll to first unanswered question
            unansweredQuestions[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Highlight unanswered questions
            unansweredQuestions.forEach(question => {
                question.classList.add('unanswered-highlight');
                setTimeout(() => {
                    question.classList.remove('unanswered-highlight');
                }, 2000);
            });
        }
    });
});

function initializeQuiz() {
    // Add animation classes to questions
    const questions = document.querySelectorAll('.quiz-question');
    questions.forEach((question, index) => {
        question.classList.add('animate-on-scroll');
        question.style.animationDelay = `${index * 0.2}s`;
    });
    
    // Initialize progress bar
    updateQuizProgress();
    
    // Add event for "Start Quiz" button if it exists
    const startButton = document.getElementById('start-quiz');
    if (startButton) {
        startButton.addEventListener('click', function() {
            const introSection = document.getElementById('quiz-intro');
            const questionsSection = document.getElementById('quiz-questions');
            
            if (introSection && questionsSection) {
                introSection.classList.add('d-none');
                questionsSection.classList.remove('d-none');
                
                // Scroll to questions
                questionsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
    
    // Check if we need to render quiz history chart
    const quizHistoryChart = document.getElementById('quiz-history-chart');
    if (quizHistoryChart && typeof initializeQuizHistoryChart === 'function') {
        const quizResults = JSON.parse(quizHistoryChart.getAttribute('data-quiz-results') || '[]');
        if (quizResults.length > 0) {
            initializeQuizHistoryChart('quiz-history-chart', quizResults);
        }
    }
}

function updateQuizProgress() {
    const questions = document.querySelectorAll('.quiz-question');
    const answeredQuestions = Array.from(questions).filter(question => {
        const questionId = question.getAttribute('data-question');
        const selectedOption = document.querySelector(`input[name="${questionId}"]:checked`);
        
        if (selectedOption) {
            question.classList.add('answered');
            return true;
        } else {
            question.classList.remove('answered');
            return false;
        }
    });
    
    // Update progress bar
    const progressBar = document.getElementById('quiz-progress-bar');
    if (progressBar) {
        const progressPercentage = (answeredQuestions.length / questions.length) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        progressBar.setAttribute('aria-valuenow', progressPercentage);
        
        // Update progress text
        const progressText = document.getElementById('quiz-progress-text');
        if (progressText) {
            progressText.textContent = `${answeredQuestions.length} de ${questions.length} perguntas respondidas`;
        }
    }
    
    // Enable/disable submit button
    const submitButton = document.getElementById('quiz-submit');
    if (submitButton) {
        if (answeredQuestions.length === questions.length) {
            submitButton.disabled = false;
            submitButton.classList.remove('btn-secondary');
            submitButton.classList.add('btn-primary');
        } else {
            submitButton.disabled = true;
            submitButton.classList.remove('btn-primary');
            submitButton.classList.add('btn-secondary');
        }
    }
}

// Quiz result animations
function animateQuizResult() {
    const resultElement = document.getElementById('quiz-result');
    if (!resultElement) return;
    
    // Add fade-in animation
    resultElement.classList.add('fade-in');
    
    // Animate score counter
    const scoreElement = document.querySelector('.quiz-score');
    if (scoreElement) {
        const finalScore = parseInt(scoreElement.getAttribute('data-score') || '0');
        let currentScore = 0;
        
        const interval = setInterval(() => {
            scoreElement.textContent = currentScore;
            currentScore++;
            
            if (currentScore > finalScore) {
                clearInterval(interval);
                scoreElement.textContent = finalScore;
                
                // Trigger level animation after score is done
                animateFanLevel();
            }
        }, 200);
    }
}

function animateFanLevel() {
    const levelElement = document.querySelector('.quiz-level');
    if (!levelElement) return;
    
    levelElement.classList.add('fade-in');
    
    // Add confetti effect for high scores
    const score = parseInt(document.querySelector('.quiz-score').getAttribute('data-score') || '0');
    if (score >= 4) {
        createConfetti();
    }
}

function createConfetti() {
    const container = document.createElement('div');
    container.className = 'confetti-container';
    document.body.appendChild(container);
    
    const colors = ['#FF0057', '#00FFB7', '#00A3FF', '#FFCC00', '#FFFFFF'];
    
    // Create confetti pieces
    for (let i = 0; i < 100; i++) {
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

// If the page loads with quiz results already shown, animate them
if (document.getElementById('quiz-result')) {
    window.addEventListener('load', animateQuizResult);
}
