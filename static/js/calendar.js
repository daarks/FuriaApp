/**
 * FURIA Know Your Fan - Calendar
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar when DOM is loaded
    initializeCalendar();
    
    // Add event listeners for filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    if (filterButtons) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');
                filterEvents(filter);
                
                // Update active state of buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
});

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    // Get user interests for filtering
    const userInterests = calendarEl.getAttribute('data-interests') ? 
        JSON.parse(calendarEl.getAttribute('data-interests')) : [];
    
    // Get favorite events
    const favoriteIds = calendarEl.getAttribute('data-favorites') ? 
        JSON.parse(calendarEl.getAttribute('data-favorites')) : [];
    
    // Fetch events data
    fetch('/static/js/events.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load events data');
            }
            return response.json();
        })
        .then(events => {
            // Initialize FullCalendar
            const calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,listMonth'
                },
                themeSystem: 'bootstrap5',
                events: formatEventsForCalendar(events, userInterests, favoriteIds),
                eventClick: function(info) {
                    showEventDetails(info.event);
                },
                eventClassNames: function(arg) {
                    const classes = [];
                    
                    // Add class for FURIA events
                    if (arg.event.extendedProps.teams && arg.event.extendedProps.teams.includes('FURIA')) {
                        classes.push('furia-event');
                    }
                    
                    // Add class for favorite events
                    if (arg.event.extendedProps.isFavorite) {
                        classes.push('favorite-event');
                    }
                    
                    return classes;
                },
                // Custom rendering
                eventContent: function(arg) {
                    const event = arg.event;
                    const isFavorite = event.extendedProps.isFavorite;
                    const isFuriaEvent = event.extendedProps.teams && 
                                        event.extendedProps.teams.includes('FURIA');
                    
                    const eventContent = document.createElement('div');
                    eventContent.className = 'fc-event-content d-flex align-items-center';
                    
                    // Add favorite star if favorite
                    if (isFavorite) {
                        const starIcon = document.createElement('i');
                        starIcon.className = 'fas fa-star me-1 text-warning';
                        eventContent.appendChild(starIcon);
                    }
                    
                    // Add FURIA badge if FURIA is playing
                    if (isFuriaEvent) {
                        const furiaIcon = document.createElement('span');
                        furiaIcon.className = 'badge bg-furia-primary me-1';
                        furiaIcon.textContent = 'FURIA';
                        eventContent.appendChild(furiaIcon);
                    }
                    
                    // Add event title
                    const titleEl = document.createElement('span');
                    titleEl.className = 'fc-event-title';
                    titleEl.textContent = event.title;
                    eventContent.appendChild(titleEl);
                    
                    return { domNodes: [eventContent] };
                }
            });
            
            calendar.render();
            
            // Add responsive handling for mobile
            window.addEventListener('resize', function() {
                const width = window.innerWidth;
                if (width < 768) {
                    calendar.changeView('listMonth');
                } else {
                    calendar.changeView('dayGridMonth');
                }
            });
            
            // Trigger initial resize handler
            if (window.innerWidth < 768) {
                calendar.changeView('listMonth');
            }
            
            // Store calendar instance for later use
            window.furiaCalendar = calendar;
        })
        .catch(error => {
            console.error('Error loading calendar events:', error);
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-danger';
            errorMessage.textContent = 'Failed to load events data. Please try again later.';
            calendarEl.parentNode.insertBefore(errorMessage, calendarEl);
        });
}

function formatEventsForCalendar(events, userInterests, favoriteIds) {
    return events.map(event => {
        // Check if the event matches user interests
        const matchesInterests = event.tags && event.tags.some(tag => userInterests.includes(tag));
        
        // Check if the event is a favorite
        const isFavorite = favoriteIds.includes(event.id);
        
        // Create event object for FullCalendar
        return {
            id: event.id,
            title: event.title,
            start: event.date,
            end: event.end_date,
            allDay: true,
            display: matchesInterests ? 'block' : 'list',
            color: matchesInterests ? '#FF0057' : '#333333',
            textColor: '#FFFFFF',
            extendedProps: {
                location: event.location,
                game: event.game,
                teams: event.teams,
                description: event.description,
                tags: event.tags,
                isFavorite: isFavorite,
                matchesInterests: matchesInterests
            }
        };
    });
}

function showEventDetails(event) {
    // Get event properties
    const props = event.extendedProps;
    const eventId = event.id;
    const isFavorite = props.isFavorite;
    
    // Create modal content
    const modalBody = `
        <div class="event-detail-header mb-3">
            <h5 class="event-game">${props.game}</h5>
            <p class="event-date">${formatDateRange(event.start, event.end)}</p>
            <p class="event-location"><i class="fas fa-map-marker-alt me-2"></i>${props.location}</p>
        </div>
        <div class="event-detail-body mb-3">
            <p>${props.description}</p>
            ${props.teams && props.teams.length ? `
                <div class="event-teams mt-3">
                    <h6>Participating Teams:</h6>
                    <ul class="list-inline">
                        ${props.teams.map(team => `
                            <li class="list-inline-item">
                                <span class="badge ${team === 'FURIA' ? 'bg-furia-primary' : 'bg-furia-dark-grey'}">
                                    ${team}
                                </span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            ${props.tags && props.tags.length ? `
                <div class="event-tags mt-3">
                    <h6>Tags:</h6>
                    <div class="tags">
                        ${props.tags.map(tag => `
                            <span class="badge bg-furia-secondary text-dark me-1">#${tag}</span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    // Create modal footer with favorite button
    const modalFooter = `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn ${isFavorite ? 'btn-warning' : 'btn-outline-warning'} toggle-favorite" 
                data-event-id="${eventId}">
            <i class="fas ${isFavorite ? 'fa-star' : 'fa-star-o'}"></i> 
            ${isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
        </button>
    `;
    
    // Create or update the modal
    let eventModal = document.getElementById('eventModal');
    if (!eventModal) {
        eventModal = document.createElement('div');
        eventModal.className = 'modal fade';
        eventModal.id = 'eventModal';
        eventModal.tabIndex = '-1';
        eventModal.setAttribute('aria-labelledby', 'eventModalLabel');
        eventModal.setAttribute('aria-hidden', 'true');
        
        eventModal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-furia-dark-grey text-white">
                    <div class="modal-header border-furia-primary">
                        <h5 class="modal-title" id="eventModalLabel">${event.title}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">${modalBody}</div>
                    <div class="modal-footer border-furia-primary">${modalFooter}</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(eventModal);
    } else {
        eventModal.querySelector('.modal-title').textContent = event.title;
        eventModal.querySelector('.modal-body').innerHTML = modalBody;
        eventModal.querySelector('.modal-footer').innerHTML = modalFooter;
    }
    
    // Initialize the modal and show it
    const modal = new bootstrap.Modal(eventModal);
    modal.show();
    
    // Add event listener for favorite button
    const favoriteButton = eventModal.querySelector('.toggle-favorite');
    favoriteButton.addEventListener('click', function() {
        toggleFavoriteEvent(this.getAttribute('data-event-id'));
    });
}

function formatDateRange(start, end) {
    const startDate = new Date(start);
    const endDate = end ? new Date(end) : null;
    
    const options = { day: 'numeric', month: 'short', year: 'numeric' };
    
    if (endDate && startDate.toDateString() !== endDate.toDateString()) {
        return `${startDate.toLocaleDateString('pt-BR', options)} - ${endDate.toLocaleDateString('pt-BR', options)}`;
    } else {
        return startDate.toLocaleDateString('pt-BR', options);
    }
}

function toggleFavoriteEvent(eventId) {
    // Send API request to toggle favorite status
    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ event_id: eventId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to toggle favorite status');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update UI to reflect new favorite status
            const button = document.querySelector(`.toggle-favorite[data-event-id="${eventId}"]`);
            
            if (data.is_favorite) {
                button.classList.remove('btn-outline-warning');
                button.classList.add('btn-warning');
                button.innerHTML = '<i class="fas fa-star"></i> Remove from Favorites';
            } else {
                button.classList.remove('btn-warning');
                button.classList.add('btn-outline-warning');
                button.innerHTML = '<i class="fas fa-star-o"></i> Add to Favorites';
            }
            
            // Update the calendar event
            if (window.furiaCalendar) {
                const event = window.furiaCalendar.getEventById(eventId);
                if (event) {
                    event.setExtendedProp('isFavorite', data.is_favorite);
                    window.furiaCalendar.refetchEvents();
                }
            }
        } else {
            showAlert('Failed to update favorite status: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        showAlert('Failed to update favorite status. Please try again.', 'danger');
    });
}

function filterEvents(filter) {
    if (!window.furiaCalendar) return;
    
    const calendar = window.furiaCalendar;
    const events = calendar.getEvents();
    
    events.forEach(event => {
        const props = event.extendedProps;
        
        switch (filter) {
            case 'all':
                event.setProp('display', 'block');
                break;
                
            case 'favorites':
                event.setProp('display', props.isFavorite ? 'block' : 'none');
                break;
                
            case 'furia':
                const hasFuria = props.teams && props.teams.includes('FURIA');
                event.setProp('display', hasFuria ? 'block' : 'none');
                break;
                
            case 'interests':
                event.setProp('display', props.matchesInterests ? 'block' : 'none');
                break;
                
            default:
                // Filter by specific game/tag
                const matchesTag = props.tags && props.tags.includes(filter);
                const matchesGame = props.game && props.game.toLowerCase().includes(filter.toLowerCase());
                event.setProp('display', (matchesTag || matchesGame) ? 'block' : 'none');
                break;
        }
    });
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}
