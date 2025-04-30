from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField, PasswordField, DateField, TextAreaField, SelectField,
    BooleanField, RadioField, SubmitField, SelectMultipleField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional, ValidationError
import datetime

# Custom validators
def validate_cpf(form, field):
    """Basic CPF format validation"""
    cpf = field.data.replace('.', '').replace('-', '')
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValidationError('CPF must contain 11 digits')

def validate_birth_date(form, field):
    """Ensure date is in the past and person is at least 13 years old"""
    today = datetime.date.today()
    if field.data > today:
        raise ValidationError('Birth date cannot be in the future')
    
    age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
    if age < 13:
        raise ValidationError('You must be at least 13 years old')

class RegistrationForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirmar Senha', 
        validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais')]
    )
    street = StringField('Rua', validators=[DataRequired(), Length(min=3, max=100)])
    city = StringField('Cidade', validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField('Estado', validators=[DataRequired(), Length(min=2, max=50)])
    complement = StringField('Complemento', validators=[Optional(), Length(max=100)])
    cpf = StringField('CPF', validators=[DataRequired(), validate_cpf])
    birth_date = DateField('Data de Nascimento', validators=[DataRequired(), validate_birth_date])
    
    # Esports interests - will be handled in the view as checkboxes
    esports_interests = SelectMultipleField(
        'Interesses em Esports', 
        choices=[
            ('cs', 'Counter-Strike'),
            ('valorant', 'Valorant'),
            ('lol', 'League of Legends'),
            ('dota', 'Dota 2'),
            ('fortnite', 'Fortnite'),
            ('overwatch', 'Overwatch'),
            ('apex', 'Apex Legends'),
            ('rainbow6', 'Rainbow Six Siege'),
            ('freefire', 'Free Fire'),
            ('rocket_league', 'Rocket League'),
            ('fut7', 'Fut7')
        ]
    )
    
    # Events attended - will be handled in the view as checkboxes
    events_attended = SelectMultipleField(
        'Eventos que Participou no Último Ano',
        choices=[
            ('major_rio', 'CS:GO Major Rio'),
            ('esl_one', 'ESL One'),
            ('blast_premier', 'BLAST Premier'),
            ('dreamhack', 'DreamHack'),
            ('copa_brasil', 'Copa Brasil'),
            ('vct_americas', 'VCT Americas'),
            ('cbcs', 'CBCS'),
            ('cblol', 'CBLOL'),
            ('gamecon', 'GameCon Brasil'),
            ('bgc', 'Brasil Game Cup'),
            ('kings_league', 'Kings League')
        ]
    )
    
    # Purchases - will be handled in the view as checkboxes
    purchases = SelectMultipleField(
        'Compras Relacionadas a Esports no Último Ano',
        choices=[
            ('team_jersey', 'Camisa Oficial de Time'),
            ('team_merch', 'Outros Produtos Oficiais (Boné, Mousepad, etc)'),
            ('gaming_gear', 'Equipamentos Gamers (Mouse, Teclado, Headset)'),
            ('event_tickets', 'Ingressos para Eventos'),
            ('battle_pass', 'Battle Pass/Passe de Temporada'),
            ('in_game_items', 'Itens dentro de Jogos'),
            ('streaming_sub', 'Assinatura de Plataforma de Streaming'),
            ('esports_betting', 'Apostas em Esports'),
            ('gaming_chair', 'Cadeira Gamer'),
            ('gaming_pc', 'PC Gamer/Componentes')
        ]
    )
    
    submit = SubmitField('Cadastrar')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class DocumentUploadForm(FlaskForm):
    document_type = SelectField(
        'Tipo de Documento',
        choices=[
            ('rg', 'RG - Carteira de Identidade'),
            ('cnh', 'CNH - Carteira Nacional de Habilitação'),
            ('passport', 'Passaporte')
        ],
        validators=[DataRequired()]
    )
    document = FileField(
        'Enviar Documento', 
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Apenas imagens e PDF!')
        ]
    )
    submit = SubmitField('Enviar e Validar')

class SocialMediaForm(FlaskForm):
    twitter = StringField('Perfil no Twitter/X', validators=[Optional()],
                          description="Ex: https://twitter.com/FuriaGG")
    instagram = StringField('Perfil no Instagram', validators=[Optional()],
                            description="Ex: https://instagram.com/furiagg")
    twitch = StringField('Canal na Twitch', validators=[Optional()],
                         description="Ex: https://twitch.tv/furiatv")
    youtube = StringField('Canal no YouTube', validators=[Optional()],
                          description="Ex: https://youtube.com/@furiagg")
    facebook = StringField('Perfil no Facebook', validators=[Optional()],
                           description="Ex: https://facebook.com/furiagg")
    submit = SubmitField('Analisar Redes Sociais')

class ContentValidationForm(FlaskForm):
    content_url = StringField('URL do Conteúdo', validators=[DataRequired(), URL()])
    submit = SubmitField('Validar Conteúdo')

class QuizForm(FlaskForm):
    # Questions will be dynamically generated but here's a static example
    question_1 = RadioField(
        'Em que ano a FURIA Esports foi fundada?',
        choices=[('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')],
        validators=[DataRequired()]
    )
    correct_1 = HiddenField(default='2017')
    
    question_2 = RadioField(
        'Qual foi o primeiro jogo com time profissional da FURIA?',
        choices=[('cs', 'Counter-Strike'), ('lol', 'League of Legends'), ('dota', 'Dota 2'), ('rainbow6', 'Rainbow Six Siege')],
        validators=[DataRequired()]
    )
    correct_2 = HiddenField(default='cs')
    
    question_3 = RadioField(
        'Quem é o fundador da FURIA Esports?',
        choices=[
            ('fallen', 'Gabriel "FalleN" Toledo'), 
            ('jaime', 'Jaime Pádua'), 
            ('andre', 'André Akkari'), 
            ('coldzera', 'Marcelo "coldzera" David')
        ],
        validators=[DataRequired()]
    )
    correct_3 = HiddenField(default='andre')
    
    question_4 = RadioField(
        'Em qual Major de CS:GO a FURIA participou pela primeira vez?',
        choices=[
            ('katowice2019', 'IEM Katowice 2019'), 
            ('berlin2019', 'StarLadder Berlin 2019'), 
            ('rio2022', 'Rio 2022'), 
            ('antwerp2022', 'PGL Antwerp 2022')
        ],
        validators=[DataRequired()]
    )
    correct_4 = HiddenField(default='berlin2019')
    
    question_5 = RadioField(
        'Qual desses jogadores NUNCA fez parte do elenco de CS:GO da FURIA?',
        choices=[
            ('kscerato', 'Kaike "KSCERATO" Cerato'), 
            ('art', 'Andrei "arT" Piovezan'), 
            ('fer', 'Fernando "fer" Alvarenga'), 
            ('yuurih', 'Yuri "yuurih" Santos')
        ],
        validators=[DataRequired()]
    )
    correct_5 = HiddenField(default='fer')
    
    submit = SubmitField('Enviar Respostas')
