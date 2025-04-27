"""
Serviço de IA para validação de documentos
Este módulo fornece uma implementação simplificada de validação de documentos
utilizando OpenCV para processamento de imagens e técnicas básicas de OCR
"""
import os
import re
import cv2
import numpy as np
import logging
from PIL import Image
import random
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentAI:
    """
    Classe responsável pela validação de documentos através de IA
    Utiliza OpenCV para processamento de imagens e técnicas de OCR
    """
    
    def __init__(self):
        """Inicializa o serviço de DocumentAI"""
        logger.debug("Inicializando DocumentAI")
        self.confidence_threshold = 0.75
        
    def validate_document(self, file_path, user_data):
        """
        Valida um documento utilizando técnicas de IA
        
        Args:
            file_path: Caminho para o arquivo do documento
            user_data: Dicionário contendo dados do usuário para verificação
                       (deve conter 'name' e 'cpf')
                       
        Returns:
            dict: Resultado da validação com status e dados extraídos
        """
        logger.debug(f"Validando documento: {file_path}")
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return {
                "status": "rejected",
                "message": "Arquivo não encontrado",
                "extracted_data": {}
            }
        
        # Verificar o tipo de arquivo
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.pdf']:
            return {
                "status": "rejected",
                "message": "Formato de arquivo não suportado. Use JPG, PNG ou PDF.",
                "extracted_data": {}
            }
        
        try:
            # Processar imagem e extrair texto
            extracted_data = self._process_image(file_path)
            
            # Verificar os dados extraídos com os dados do usuário
            validation_result = self._verify_extracted_data(extracted_data, user_data)
            
            return validation_result
        
        except Exception as e:
            logger.error(f"Erro ao validar documento: {str(e)}")
            return {
                "status": "rejected",
                "message": f"Erro ao processar documento: {str(e)}",
                "extracted_data": {}
            }
    
    def _process_image(self, file_path):
        """
        Processa a imagem do documento e extrai texto e informações
        
        Args:
            file_path: Caminho para o arquivo de imagem
            
        Returns:
            dict: Dados extraídos da imagem
        """
        logger.debug(f"Processando imagem: {file_path}")
        
        # Simulação do processamento de imagem real
        # Em uma implementação completa, usaria OCR e técnicas avançadas
        
        # Carregar imagem
        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Não foi possível carregar a imagem")
                
            # Verificar qualidade/resolução da imagem
            height, width = img.shape[:2]
            if width < 600 or height < 400:
                logger.warning("Imagem com resolução baixa")
                image_quality = "low"
            else:
                image_quality = "high"
                
            # Converter para escala de cinza
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar limiarização para melhorar contraste
            _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Esta é uma simulação do processamento OCR
            # Em uma implementação real, usaria tesseract ou outra biblioteca OCR
            simulation_quality = random.random()
            
            # Baseado na qualidade da imagem e simulação, decidir o resultado
            if simulation_quality < 0.2 or image_quality == "low":
                # Simulação de falha na extração de dados
                return {
                    "quality": image_quality,
                    "ocr_confidence": random.uniform(0.3, 0.6),
                    "error": "Baixa qualidade de imagem ou texto não reconhecível"
                }
            
            # Simulação de extração bem-sucedida para demonstração
            return {
                "quality": image_quality,
                "ocr_confidence": random.uniform(0.75, 0.98),
                "detected_document_type": self._detect_document_type(img),
                "text_regions": self._simulate_text_regions(),
                "processed_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de imagem: {str(e)}")
            raise
    
    def _detect_document_type(self, image):
        """
        Detecta o tipo de documento baseado em características visuais
        
        Args:
            image: Imagem do documento
            
        Returns:
            str: Tipo de documento detectado
        """
        # Esta é uma simulação - em uma implementação real, usaria 
        # classificadores treinados ou reconhecimento de padrões
        
        height, width = image.shape[:2]
        aspect_ratio = width / height
        
        # Simular diferentes tipos baseado em proporções e outras características
        if aspect_ratio > 1.5:
            # Documentos como CNH têm formato mais largo
            return "cnh"
        elif 1.3 < aspect_ratio < 1.5:
            # RG e outros documentos têm essa proporção
            return "rg"
        else:
            # Formato mais quadrado como passaporte
            return "passport"
    
    def _simulate_text_regions(self):
        """
        Simula a detecção de regiões de texto em um documento
        
        Returns:
            dict: Regiões de texto detectadas com coordenadas e conteúdo
        """
        # Em uma implementação real, retornaria regiões detectadas por OCR
        return {
            "name_region": {
                "coords": [100, 150, 400, 180],
                "confidence": random.uniform(0.8, 0.95)
            },
            "document_number_region": {
                "coords": [150, 250, 350, 280],
                "confidence": random.uniform(0.8, 0.95)
            },
            "date_region": {
                "coords": [200, 300, 400, 330],
                "confidence": random.uniform(0.75, 0.9)
            }
        }
    
    def _verify_extracted_data(self, extracted_data, user_data):
        """
        Verifica os dados extraídos contra os dados do usuário
        
        Args:
            extracted_data: Dados extraídos da imagem
            user_data: Dados do usuário para verificação
            
        Returns:
            dict: Resultado da validação
        """
        logger.debug("Verificando dados extraídos")
        
        # Verificar se houve erro na extração
        if "error" in extracted_data:
            return {
                "status": "rejected",
                "message": f"Falha na extração de dados: {extracted_data['error']}",
                "extracted_data": extracted_data
            }
        
        # Verificar a confiança do OCR
        if extracted_data.get("ocr_confidence", 0) < self.confidence_threshold:
            return {
                "status": "rejected",
                "message": "Confiança do OCR abaixo do limiar aceitável. Tente novamente com uma imagem mais clara.",
                "extracted_data": {
                    "confidence_score": extracted_data.get("ocr_confidence")
                }
            }
        
        # Aqui simulamos a comparação com os dados do usuário
        # Na vida real, teríamos algoritmos de comparação de textos e similaridade
        
        match_probability = random.random()
        
        if match_probability > 0.8:
            # Alta probabilidade de correspondência - verificação bem-sucedida
            return {
                "status": "verified",
                "message": "Documento validado com sucesso",
                "extracted_data": {
                    "name": user_data.get("name"),
                    "cpf": user_data.get("cpf"),
                    "document_type": extracted_data.get("detected_document_type", "unknown"),
                    "confidence_score": extracted_data.get("ocr_confidence", 0.9),
                    "verification_timestamp": datetime.now().isoformat()
                }
            }
        elif match_probability > 0.4:
            # Correspondência parcial - resultados ambíguos
            modified_name = self._create_variation(user_data.get("name", ""))
            modified_cpf = self._create_variation(user_data.get("cpf", ""))
            
            return {
                "status": "pending",
                "message": "Documento parcialmente validado. Alguns dados não correspondem exatamente.",
                "extracted_data": {
                    "name": modified_name,
                    "cpf": modified_cpf,
                    "document_type": extracted_data.get("detected_document_type", "unknown"),
                    "confidence_score": extracted_data.get("ocr_confidence", 0.7),
                    "verification_timestamp": datetime.now().isoformat()
                }
            }
        else:
            # Baixa correspondência - rejeição
            return {
                "status": "rejected",
                "message": "Os dados do documento não correspondem aos dados registrados.",
                "extracted_data": {
                    "confidence_score": extracted_data.get("ocr_confidence", 0.5),
                    "verification_timestamp": datetime.now().isoformat()
                }
            }
    
    def _create_variation(self, text):
        """
        Cria uma pequena variação em um texto para simular erros de OCR
        
        Args:
            text: Texto original
            
        Returns:
            str: Texto com pequenas variações
        """
        if not text or len(text) < 3:
            return text
            
        # Decide qual tipo de variação aplicar
        variation_type = random.choice(["char_swap", "char_remove", "char_add", "none"])
        
        if variation_type == "none" or len(text) < 2:
            return text
            
        if variation_type == "char_swap" and len(text) >= 2:
            # Trocar dois caracteres adjacentes
            pos = random.randint(0, len(text) - 2)
            chars = list(text)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            return ''.join(chars)
            
        elif variation_type == "char_remove":
            # Remover um caractere
            pos = random.randint(0, len(text) - 1)
            return text[:pos] + text[pos+1:]
            
        elif variation_type == "char_add":
            # Adicionar um caractere
            pos = random.randint(0, len(text))
            char_to_add = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            return text[:pos] + char_to_add + text[pos:]
            
        return text

# Criar instância global para uso no aplicativo
document_ai = DocumentAI()