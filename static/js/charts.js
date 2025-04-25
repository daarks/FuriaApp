/**
 * FURIA Know Your Fan - Charts
 */

function initializeFanPowerChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fan Power'],
            datasets: [{
                label: 'Fan Power Score',
                data: [data.overall_score, 100 - data.overall_score],
                backgroundColor: [
                    '#FF0057',
                    'rgba(255, 255, 255, 0.1)'
                ],
                borderColor: [
                    '#FF0057',
                    'transparent'
                ],
                borderWidth: 1,
                cutout: '80%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true
            }
        }
    });
    
    // Add center text
    Chart.register({
        id: 'centerText',
        beforeDraw: function(chart) {
            const width = chart.width;
            const height = chart.height;
            const ctx = chart.ctx;
            
            ctx.restore();
            const fontSize = (height / 114).toFixed(2);
            ctx.font = fontSize + 'em sans-serif';
            ctx.fillStyle = '#FFFFFF';
            ctx.textBaseline = 'middle';
            
            const score = data.overall_score.toFixed(0);
            const text = score + '%';
            const textX = Math.round((width - ctx.measureText(text).width) / 2);
            const textY = height / 2;
            
            ctx.fillText(text, textX, textY);
            
            // Add category text
            ctx.font = (fontSize * 0.5) + 'em sans-serif';
            ctx.fillStyle = '#00FFB7';
            
            const categoryText = data.fan_category;
            const categoryTextX = Math.round((width - ctx.measureText(categoryText).width) / 2);
            const categoryTextY = height / 2 + 30;
            
            ctx.fillText(categoryText, categoryTextX, categoryTextY);
            
            ctx.save();
        }
    });
    
    return chart;
}

function initializeMetricsChart(elementId, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Engajamento Social', 
                'Consumo de Conteúdo', 
                'Participação em Eventos', 
                'Suporte com Merchandise'
            ],
            datasets: [{
                label: 'Métricas de Engajamento',
                data: [
                    data.social_engagement,
                    data.content_consumption,
                    data.event_participation,
                    data.merchandise_support
                ],
                backgroundColor: 'rgba(0, 255, 183, 0.2)',
                borderColor: '#00FFB7',
                borderWidth: 2,
                pointBackgroundColor: '#00FFB7',
                pointBorderColor: '#FFFFFF',
                pointHoverBackgroundColor: '#FFFFFF',
                pointHoverBorderColor: '#00FFB7'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#FFFFFF',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        beginAtZero: true,
                        max: 100,
                        stepSize: 20,
                        backdropColor: 'transparent',
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    return chart;
}

function initializeQuizHistoryChart(elementId, quizResults) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Parse quiz results
    const labels = [];
    const scores = [];
    
    quizResults.forEach((result, index) => {
        // Format date for label - this assumes result.created_at is in ISO format
        const date = new Date(result.created_at);
        const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
        
        labels.push(`Tentativa ${index + 1} (${formattedDate})`);
        scores.push(result.score);
    });
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pontuação',
                data: scores,
                backgroundColor: 'rgba(255, 0, 87, 0.2)',
                borderColor: '#FF0057',
                borderWidth: 2,
                pointBackgroundColor: '#FF0057',
                pointBorderColor: '#FFFFFF',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    return chart;
}

function initializeSocialEngagementChart(elementId, socialMediaData) {
    if (!socialMediaData || !socialMediaData.interactions) {
        return null;
    }
    
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Parse interaction data
    const interactions = JSON.parse(socialMediaData.interactions);
    const labels = Object.keys(interactions);
    const data = labels.map(key => interactions[key].count);
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
            datasets: [{
                label: 'Interações',
                data: data,
                backgroundColor: [
                    'rgba(255, 0, 87, 0.7)',
                    'rgba(0, 255, 183, 0.7)',
                    'rgba(0, 163, 255, 0.7)',
                    'rgba(255, 204, 0, 0.7)'
                ],
                borderColor: [
                    '#FF0057',
                    '#00FFB7',
                    '#00A3FF',
                    '#FFCC00'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    return chart;
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fan Power Gauge
    const fanPowerElement = document.getElementById('fan-power-gauge');
    if (fanPowerElement) {
        const fanPowerData = JSON.parse(fanPowerElement.getAttribute('data-metrics'));
        initializeFanPowerChart('fan-power-gauge', fanPowerData);
    }
    
    // Metrics Chart
    const metricsElement = document.getElementById('metrics-chart');
    if (metricsElement) {
        const metricsData = JSON.parse(metricsElement.getAttribute('data-metrics'));
        initializeMetricsChart('metrics-chart', metricsData);
    }
    
    // Quiz History Chart
    const quizHistoryElement = document.getElementById('quiz-history-chart');
    if (quizHistoryElement) {
        const quizData = JSON.parse(quizHistoryElement.getAttribute('data-quiz-results'));
        initializeQuizHistoryChart('quiz-history-chart', quizData);
    }
    
    // Social Engagement Chart
    const socialEngagementElement = document.getElementById('social-engagement-chart');
    if (socialEngagementElement) {
        const socialData = JSON.parse(socialEngagementElement.getAttribute('data-social-media'));
        initializeSocialEngagementChart('social-engagement-chart', socialData);
    }
});
