/**
 * FURIA Know Your Fan - Document Validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // File input preview and validation
    const fileInput = document.getElementById('document');
    if (fileInput) {
        fileInput.addEventListener('change', previewDocument);
    }
    
    // Form submission handling
    const documentForm = document.getElementById('document-form');
    if (documentForm) {
        documentForm.addEventListener('submit', function(event) {
            if (!validateDocumentForm()) {
                event.preventDefault();
            } else {
                // Show loading state
                showValidationInProgress();
            }
        });
    }
    
    // Document type selection
    const documentTypeSelect = document.getElementById('document_type');
    if (documentTypeSelect) {
        documentTypeSelect.addEventListener('change', updateDocumentRequirements);
        // Initialize on load
        updateDocumentRequirements();
    }
    
    // Initialize tooltips for document status
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggers.forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });
    
    // Check if validation result is present and show details
    const validationResult = document.getElementById('validation-result');
    if (validationResult && validationResult.dataset.status) {
        showValidationDetails(
            validationResult.dataset.status,
            JSON.parse(validationResult.dataset.details || '{}')
        );
    }
});

function previewDocument(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showAlert('Por favor, envie apenas arquivos JPG, PNG ou PDF.', 'danger');
        event.target.value = ''; // Clear the file input
        clearPreview();
        return;
    }
    
    // Check file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showAlert('O arquivo é muito grande. O tamanho máximo é 5MB.', 'danger');
        event.target.value = ''; // Clear the file input
        clearPreview();
        return;
    }
    
    // Update file name display
    const fileNameDisplay = document.getElementById('file-name');
    if (fileNameDisplay) {
        fileNameDisplay.textContent = file.name;
    }
    
    // If it's an image, show preview
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const previewContainer = document.getElementById('document-preview');
            if (previewContainer) {
                previewContainer.innerHTML = `
                    <div class="card bg-furia-grey mb-3">
                        <div class="card-header">Document Preview</div>
                        <div class="card-body text-center">
                            <img src="${e.target.result}" class="img-fluid document-image" alt="Document preview">
                        </div>
                    </div>
                `;
                previewContainer.classList.remove('d-none');
            }
        };
        
        reader.readAsDataURL(file);
    } else if (file.type === 'application/pdf') {
        // For PDF, just show an icon
        const previewContainer = document.getElementById('document-preview');
        if (previewContainer) {
            previewContainer.innerHTML = `
                <div class="card bg-furia-grey mb-3">
                    <div class="card-header">Document Preview</div>
                    <div class="card-body text-center">
                        <i class="fas fa-file-pdf fa-5x text-furia-primary mb-3"></i>
                        <p class="mb-0">${file.name}</p>
                    </div>
                </div>
            `;
            previewContainer.classList.remove('d-none');
        }
    }
    
    // Enable submit button
    const submitButton = document.getElementById('submit-button');
    if (submitButton) {
        submitButton.disabled = false;
    }
}

function clearPreview() {
    const previewContainer = document.getElementById('document-preview');
    if (previewContainer) {
        previewContainer.innerHTML = '';
        previewContainer.classList.add('d-none');
    }
    
    const fileNameDisplay = document.getElementById('file-name');
    if (fileNameDisplay) {
        fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
    }
    
    // Disable submit button
    const submitButton = document.getElementById('submit-button');
    if (submitButton) {
        submitButton.disabled = true;
    }
}

function validateDocumentForm() {
    const fileInput = document.getElementById('document');
    const documentType = document.getElementById('document_type');
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        showAlert('Por favor, selecione um documento para enviar.', 'danger');
        return false;
    }
    
    if (!documentType || !documentType.value) {
        showAlert('Por favor, selecione o tipo de documento.', 'danger');
        return false;
    }
    
    return true;
}

function showValidationInProgress() {
    // Hide the form
    const form = document.getElementById('document-form');
    if (form) {
        form.classList.add('d-none');
    }
    
    // Show loading state
    const loadingContainer = document.getElementById('validation-loading');
    if (!loadingContainer) {
        const container = document.createElement('div');
        container.id = 'validation-loading';
        container.className = 'text-center my-5';
        container.innerHTML = `
            <div class="spinner-border text-furia-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h4 class="mb-3">Validando seu documento...</h4>
            <p class="text-muted">Estamos analisando seu documento com nossa tecnologia de reconhecimento ótico. Isso pode levar alguns segundos.</p>
            <div class="progress mt-3">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-furia-primary" 
                     role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        `;
        
        // Insert after form
        form.parentNode.insertBefore(container, form.nextSibling);
        
        // Animate progress bar
        const progressBar = container.querySelector('.progress-bar');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 300);
    }
}

function updateDocumentRequirements() {
    const documentType = document.getElementById('document_type');
    const requirementsContainer = document.getElementById('document-requirements');
    
    if (!documentType || !requirementsContainer) return;
    
    const selectedType = documentType.value;
    let requirementsHTML = '<ul class="list-group list-group-flush bg-transparent mb-3">';
    
    switch (selectedType) {
        case 'rg':
            requirementsHTML += `
                <li class="list-group-item bg-transparent">A imagem deve mostrar claramente a frente do RG</li>
                <li class="list-group-item bg-transparent">Verifique se o nome e CPF estão legíveis</li>
                <li class="list-group-item bg-transparent">Certifique-se de que a foto não está desfocada</li>
                <li class="list-group-item bg-transparent">Documentos digitais são aceitos</li>
            `;
            break;
        case 'cnh':
            requirementsHTML += `
                <li class="list-group-item bg-transparent">A imagem deve mostrar a CNH por completo</li>
                <li class="list-group-item bg-transparent">Verifique se o nome, CPF e categorias estão legíveis</li>
                <li class="list-group-item bg-transparent">Certifique-se de que a foto não está desfocada</li>
                <li class="list-group-item bg-transparent">CNH Digital também é aceita</li>
            `;
            break;
        case 'passport':
            requirementsHTML += `
                <li class="list-group-item bg-transparent">A imagem deve mostrar a página principal do passaporte</li>
                <li class="list-group-item bg-transparent">Verifique se o nome e número do passaporte estão legíveis</li>
                <li class="list-group-item bg-transparent">Certifique-se de que a foto não está desfocada</li>
            `;
            break;
    }
    
    requirementsHTML += '</ul>';
    requirementsContainer.innerHTML = requirementsHTML;
}

function showValidationDetails(status, details) {
    const detailsContainer = document.getElementById('validation-details');
    if (!detailsContainer) return;
    
    let statusClass, statusIcon, statusTitle;
    
    switch (status) {
        case 'verified':
            statusClass = 'success';
            statusIcon = 'check-circle';
            statusTitle = 'Documento Verificado com Sucesso';
            break;
        case 'rejected':
            statusClass = 'danger';
            statusIcon = 'times-circle';
            statusTitle = 'Falha na Verificação do Documento';
            break;
        default:
            statusClass = 'warning';
            statusIcon = 'exclamation-circle';
            statusTitle = 'Verificação de Documento Pendente';
    }
    
    let detailsHTML = `
        <div class="card bg-furia-grey mb-4">
            <div class="card-header bg-${statusClass} text-white">
                <h5 class="mb-0"><i class="fas fa-${statusIcon} me-2"></i> ${statusTitle}</h5>
            </div>
            <div class="card-body">
    `;
    
    if (status === 'verified') {
        detailsHTML += `
            <p class="mb-3">Seu documento foi verificado com sucesso. Os dados correspondem ao seu cadastro.</p>
            <div class="verified-details">
                <div class="mb-3">
                    <h6 class="text-furia-secondary">Confiança da verificação:</h6>
                    <div class="progress">
                        <div class="progress-bar bg-success" role="progressbar" 
                             style="width: ${details.extracted_data?.confidence_score * 100}%" 
                             aria-valuenow="${details.extracted_data?.confidence_score * 100}" 
                             aria-valuemin="0" aria-valuemax="100">
                            ${Math.round(details.extracted_data?.confidence_score * 100)}%
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <h6 class="text-furia-secondary">Nome Verificado:</h6>
                        <p class="mb-0">${details.extracted_data?.name || 'N/A'}</p>
                    </div>
                    <div class="col-md-6 mb-3">
                        <h6 class="text-furia-secondary">CPF Verificado:</h6>
                        <p class="mb-0">${details.extracted_data?.cpf || 'N/A'}</p>
                    </div>
                </div>
            </div>
        `;
    } else if (status === 'rejected') {
        detailsHTML += `
            <p class="mb-3">Não foi possível verificar seu documento. Por favor, verifique os detalhes abaixo e tente novamente.</p>
            <div class="alert alert-danger">
                <strong>Motivo da rejeição:</strong> ${details.message || 'Erro de verificação'}
            </div>
        `;
        
        if (details.extracted_data) {
            detailsHTML += `
                <div class="rejected-details mt-3">
                    <h6 class="text-furia-secondary mb-2">Detalhes da tentativa:</h6>
                    <div class="mb-3">
                        <h6 class="text-furia-secondary">Confiança da análise:</h6>
                        <div class="progress">
                            <div class="progress-bar bg-warning" role="progressbar" 
                                 style="width: ${details.extracted_data?.confidence_score * 100}%" 
                                 aria-valuenow="${details.extracted_data?.confidence_score * 100}" 
                                 aria-valuemin="0" aria-valuemax="100">
                                ${Math.round(details.extracted_data?.confidence_score * 100)}%
                            </div>
                        </div>
                    </div>
            `;
            
            if (details.extracted_data.name) {
                detailsHTML += `
                    <div class="mb-2">
                        <h6 class="text-furia-secondary">Nome Extraído:</h6>
                        <p class="mb-0">${details.extracted_data.name}</p>
                    </div>
                `;
            }
            
            if (details.extracted_data.cpf) {
                detailsHTML += `
                    <div class="mb-2">
                        <h6 class="text-furia-secondary">CPF Extraído:</h6>
                        <p class="mb-0">${details.extracted_data.cpf}</p>
                    </div>
                `;
            }
            
            detailsHTML += `</div>`;
        }
        
        detailsHTML += `
            <div class="mt-4">
                <h6 class="text-furia-secondary mb-2">Dicas para uma verificação bem-sucedida:</h6>
                <ul class="list-group list-group-flush bg-transparent">
                    <li class="list-group-item bg-transparent">Certifique-se de que o documento está em uma superfície plana</li>
                    <li class="list-group-item bg-transparent">Garanta que há boa iluminação</li>
                    <li class="list-group-item bg-transparent">Verifique se o documento está completamente visível na imagem</li>
                    <li class="list-group-item bg-transparent">Utilize uma imagem com alta resolução</li>
                </ul>
            </div>
        `;
    } else {
        detailsHTML += `
            <p>Seu documento ainda não foi verificado. Por favor, envie um documento válido.</p>
        `;
    }
    
    detailsHTML += `
            </div>
            <div class="card-footer bg-transparent">
                <button id="try-again-button" class="btn btn-primary">Enviar Novo Documento</button>
            </div>
        </div>
    `;
    
    detailsContainer.innerHTML = detailsHTML;
    
    // Add event listener for try again button
    const tryAgainButton = document.getElementById('try-again-button');
    if (tryAgainButton) {
        tryAgainButton.addEventListener('click', function() {
            // Hide details container
            detailsContainer.classList.add('d-none');
            
            // Show form
            const form = document.getElementById('document-form');
            if (form) {
                form.classList.remove('d-none');
            }
        });
    }
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('document-alerts');
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
