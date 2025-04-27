from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField, PasswordField, DateField, TextAreaField, SelectField,
    BooleanField, RadioField, SubmitField, SelectMultipleField, HiddenField,
    IntegerField
)
from wtforms.validators import NumberRange
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
    name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    cpf = StringField('CPF', validators=[DataRequired(), validate_cpf])
    birth_date = DateField('Birth Date', validators=[DataRequired(), validate_birth_date])
    
    # Esports interests - will be handled in the view as checkboxes
    esports_interests = SelectMultipleField(
        'Esports Interests', 
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
            ('rocket_league', 'Rocket League')
        ]
    )
    
    # Events attended - will be handled in the view as checkboxes
    events_attended = SelectMultipleField(
        'Events Attended in the Last Year',
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
            ('bgc', 'Brasil Game Cup')
        ]
    )
    
    # Purchases - will be handled in the view as checkboxes
    purchases = SelectMultipleField(
        'Purchases Related to Esports in the Last Year',
        choices=[
            ('team_jersey', 'Team Jersey'),
            ('team_merch', 'Other Team Merchandise'),
            ('gaming_gear', 'Gaming Gear'),
            ('event_tickets', 'Event Tickets'),
            ('battle_pass', 'Battle Pass/Season Pass'),
            ('in_game_items', 'In-game Items'),
            ('streaming_sub', 'Streaming Subscription'),
            ('esports_betting', 'Esports Betting'),
            ('gaming_chair', 'Gaming Chair'),
            ('gaming_pc', 'Gaming PC/Components')
        ]
    )
    
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DocumentUploadForm(FlaskForm):
    document_type = SelectField(
        'Document Type',
        choices=[
            ('rg', 'RG - Identity Card'),
            ('cnh', 'CNH - Driver\'s License'),
            ('passport', 'Passport')
        ],
        validators=[DataRequired()]
    )
    document = FileField(
        'Upload Document', 
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
        ]
    )
    submit = SubmitField('Upload and Validate')

class SocialMediaForm(FlaskForm):
    twitter = StringField('Twitter/X Profile', validators=[Optional()],
                          description="Ex: https://twitter.com/FuriaGG")
    instagram = StringField('Instagram Profile', validators=[Optional()],
                            description="Ex: https://instagram.com/furiagg")
    twitch = StringField('Twitch Channel', validators=[Optional()],
                         description="Ex: https://twitch.tv/furiatv")
    youtube = StringField('YouTube Channel', validators=[Optional()],
                          description="Ex: https://youtube.com/@furiagg")
    facebook = StringField('Facebook Profile', validators=[Optional()],
                           description="Ex: https://facebook.com/furiagg")
    submit = SubmitField('Analisar Redes Sociais')

class ContentValidationForm(FlaskForm):
    content_url = StringField('Content URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Validate Content')

class MatchPredictionForm(FlaskForm):
    """Formulário para previsão de resultados de partidas (Bolão)"""
    furia_score = IntegerField('Pontuação FURIA', validators=[
        DataRequired(),
        NumberRange(min=0, max=50, message='Pontuação deve estar entre 0 e 50')
    ])
    opponent_score = IntegerField('Pontuação Adversário', validators=[
        DataRequired(),
        NumberRange(min=0, max=50, message='Pontuação deve estar entre 0 e 50')
    ])
    predicted_mvp = SelectField('MVP da FURIA', validators=[DataRequired()], choices=[])
    predicted_opponent_highlight = StringField('Destaque do Adversário', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Enviar Palpite')
    
    def set_player_choices(self, players):
        """Configura as opções de jogadores da FURIA para MVP"""
        self.predicted_mvp.choices = [(p, p) for p in players]

class QuizForm(FlaskForm):
    # Questions will be dynamically generated but here's a static example
    question_1 = RadioField(
        'Which year was FURIA Esports founded?',
        choices=[('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')],
        validators=[DataRequired()]
    )
    correct_1 = HiddenField(default='2017')
    
    question_2 = RadioField(
        'Which game was FURIA\'s first professional team?',
        choices=[('cs', 'Counter-Strike'), ('lol', 'League of Legends'), ('dota', 'Dota 2'), ('rainbow6', 'Rainbow Six Siege')],
        validators=[DataRequired()]
    )
    correct_2 = HiddenField(default='cs')
    
    question_3 = RadioField(
        'Who is the founder of FURIA Esports?',
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
        'In which CS:GO Major did FURIA first participate?',
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
        'Which of these players has NEVER been part of FURIA\'s CS:GO roster?',
        choices=[
            ('kscerato', 'Kaike "KSCERATO" Cerato'), 
            ('art', 'Andrei "arT" Piovezan'), 
            ('fer', 'Fernando "fer" Alvarenga'), 
            ('yuurih', 'Yuri "yuurih" Santos')
        ],
        validators=[DataRequired()]
    )
    correct_5 = HiddenField(default='fer')
    
    submit = SubmitField('Submit Quiz')
