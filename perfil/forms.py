from dataclasses import fields
from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = '__all__'
        exclude = ('usuario', )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha',
        # help_text='' # mandar ajuda para a senha
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação Senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msg = {}

        # consultas abaixo veem do formulário e não do DB (até linha 47)
        # usuario_data = data['username'] # outro jeito de buscar a informação
        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        # cobsulta no banco de dados
        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = 'Usuário já existe'
        error_msg_email_exists = 'Email já existe'
        error_msg_password_match = 'As senhas não conferem'
        error_msg_password_short = 'Sua senha precisa de minimo 6 caractres'
        error_msg_required_field = 'Esse campo é obrigatório'

        # Usuários logados
        if self.usuario:
            if usuario_db:
                # nesse ponto o professor colocou .username (não entendi)
                if usuario_data != usuario_db.username:
                    print('AQUI!!')
                    print(usuario_data)
                    print(usuario_db)
                    validation_error_msg['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msg['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msg['password'] = error_msg_password_match
                    validation_error_msg['password2'] = error_msg_password_match

                if len(password_data) < 6:
                    validation_error_msg['password'] = error_msg_password_short

        # Usuário não logados
        else:

            if usuario_db:
                validation_error_msg['username'] = error_msg_user_exists

            if email_db:
                validation_error_msg['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msg['password'] = error_msg_required_field

            if not password2_data:
                validation_error_msg['password2'] = error_msg_required_field

            if password_data != password2_data:
                validation_error_msg['password'] = error_msg_password_match
                validation_error_msg['password2'] = error_msg_password_match

            if len(password_data) < 6:
                validation_error_msg['password'] = error_msg_password_short

        if validation_error_msg:
            raise(forms.ValidationError(validation_error_msg))
