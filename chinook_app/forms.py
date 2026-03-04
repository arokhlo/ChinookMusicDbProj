from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from allauth.account.forms import (
    LoginForm, SignupForm, ResetPasswordForm, ResetPasswordKeyForm
)
from .models import Artist, Album, Review, UserProfile, SecurityQuestion

User = get_user_model()

# Add this class to the end of the file
class SecurityQuestionSetupForm(forms.Form):
    """Form for setting up security questions for existing users."""
    
    # Security Questions Fields
    question_1 = forms.ChoiceField(
        choices=[],
        label="Security Question 1",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    answer_1 = forms.CharField(
        max_length=255,
        label="Answer 1",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    question_2 = forms.ChoiceField(
        choices=[],
        label="Security Question 2",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    answer_2 = forms.CharField(
        max_length=255,
        label="Answer 2",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    question_3 = forms.ChoiceField(
        choices=[],
        label="Security Question 3",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    answer_3 = forms.CharField(
        max_length=255,
        label="Answer 3",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    question_4 = forms.ChoiceField(
        choices=[],
        label="Security Question 4",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    answer_4 = forms.CharField(
        max_length=255,
        label="Answer 4",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    question_5 = forms.ChoiceField(
        choices=[],
        label="Security Question 5",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    answer_5 = forms.CharField(
        max_length=255,
        label="Answer 5",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all available questions from the SecurityQuestion model
        from .models import SecurityQuestion
        question_choices = SecurityQuestion.QUESTION_CHOICES.copy()

        # Initialize all question fields with the same choices
        for i in range(1, 6):
            self.fields[f'question_{i}'].choices = [
                ('', '---------')
            ] + question_choices

    def clean(self):
        cleaned_data = super().clean()

        # Check for duplicate questions
        questions = []
        for i in range(1, 6):
            question = cleaned_data.get(f'question_{i}')
            if question:
                questions.append(question)

        # Check for duplicates
        if len(questions) != len(set(questions)):
            raise forms.ValidationError(
                "You cannot select the same security question multiple times. "
                "Please choose different questions."
            )

        # Validate that answers are provided for all questions
        for i in range(1, 6):
            question = cleaned_data.get(f'question_{i}')
            answer = cleaned_data.get(f'answer_{i}')

            if question and (not answer or not answer.strip()):
                self.add_error(
                    f'answer_{i}',
                    'This field is required when a question is selected.'
                )
            elif not question and answer:
                self.add_error(
                    f'question_{i}',
                    'Please select a question for this answer.'
                )

        return cleaned_data

class SetNewPasswordForm(forms.Form):
    """Form for setting new password after security question verification."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if (new_password and confirm_password
                and new_password != confirm_password):
            raise forms.ValidationError("Passwords don't match.")

        return cleaned_data


class CustomResetPasswordForm(ResetPasswordForm):
    """
    Custom password reset form that uses username and redirects to security
    questions instead of sending emails.
    """
    username = forms.CharField(
        max_length=150,
        label="Username",
        help_text=(
            "Enter your username to reset password "
            "using security questions"
        ),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the email field from the parent class
        self.fields.pop('email', None)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                # Check if user has security questions
                if not SecurityQuestion.objects.filter(user=user).exists():
                    raise ValidationError(
                        "Security questions not found for this user. "
                        "Please contact admin at mortazazolfpour@gmail.com."
                    )
            except User.DoesNotExist:
                raise ValidationError(
                    "User not found. Please check the username."
                )
        return username

    def save(self, request, **kwargs):
        """Override save to return username for security question flow."""
        username = self.cleaned_data["username"]
        return username


class SecurityQuestionResetForm(forms.Form):
    """Form for initiating password reset with username."""
    username = forms.CharField(
        max_length=150,
        label="Username",
        help_text=(
            "Enter your username to reset password "
            "using security questions"
        ),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                # Check if user has security questions
                if not SecurityQuestion.objects.filter(user=user).exists():
                    raise ValidationError(
                        "Security questions not found for this user. "
                        "Please contact admin at mortazazolfpour@gmail.com."
                    )
            except User.DoesNotExist:
                raise ValidationError(
                    "User not found. Please check the username."
                )
        return username


class SecurityQuestionVerificationForm(forms.Form):
    """Form for verifying security question answers."""

    def __init__(self, *args, **kwargs):
        security_questions = kwargs.pop('security_questions', [])
        super().__init__(*args, **kwargs)

        for i, question_data in enumerate(security_questions):
            question_text = question_data['question']

            self.fields[f'answer_{i+1}'] = forms.CharField(
                max_length=255,
                label=f"Question {i+1}: {question_text}",
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your answer'
                }),
                required=True
            )

    def clean(self):
        cleaned_data = super().clean()
        # Ensure all answer fields are filled
        for field_name, value in cleaned_data.items():
            if field_name.startswith('answer_') and not value:
                self.add_error(field_name, 'This field is required.')
        return cleaned_data


class CustomSignupForm(SignupForm):
    """
    Custom signup form with 5 security questions and dynamic filtering.
    """
    # Security Questions Fields - initialize with empty choices
    question_1 = forms.ChoiceField(
        choices=[],
        label="Security Question 1",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    answer_1 = forms.CharField(
        max_length=255,
        label="Answer 1",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    question_2 = forms.ChoiceField(
        choices=[],
        label="Security Question 2",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    answer_2 = forms.CharField(
        max_length=255,
        label="Answer 2",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    question_3 = forms.ChoiceField(
        choices=[],
        label="Security Question 3",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    answer_3 = forms.CharField(
        max_length=255,
        label="Answer 3",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    question_4 = forms.ChoiceField(
        choices=[],
        label="Security Question 4",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    answer_4 = forms.CharField(
        max_length=255,
        label="Answer 4",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    question_5 = forms.ChoiceField(
        choices=[],
        label="Security Question 5",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    answer_5 = forms.CharField(
        max_length=255,
        label="Answer 5",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all available questions
        question_choices = SecurityQuestion.QUESTION_CHOICES.copy()

        # Initialize all question fields with the same choices
        for i in range(1, 6):
            self.fields[f'question_{i}'].choices = [
                ('', '---------')
            ] + question_choices

        # Add Bootstrap classes to allauth fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                "A user with this username already exists. "
                "Please choose a different username."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "A user with this email address already exists. "
                "Please use a different email."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()

        # Check for duplicate questions
        questions = []
        for i in range(1, 6):
            question = cleaned_data.get(f'question_{i}')
            if question:
                questions.append(question)

        # Check for duplicates
        if len(questions) != len(set(questions)):
            raise forms.ValidationError(
                "You cannot select the same security question multiple times. "
                "Please choose different questions."
            )

        # Validate that answers are provided for all questions
        for i in range(1, 6):
            question = cleaned_data.get(f'question_{i}')
            answer = cleaned_data.get(f'answer_{i}')

            if question and (not answer or not answer.strip()):
                self.add_error(
                    f'answer_{i}',
                    'This field is required when a question is selected.'
                )
            elif not question and answer:
                self.add_error(
                    f'question_{i}',
                    'Please select a question for this answer.'
                )

        return cleaned_data

    def save(self, request):
        user = super().save(request)

        # Create security questions
        security_questions = SecurityQuestion(
            user=user,
            question_1=self.cleaned_data['question_1'],
            answer_1=self.cleaned_data['answer_1'].lower().strip(),
            question_2=self.cleaned_data['question_2'],
            answer_2=self.cleaned_data['answer_2'].lower().strip(),
            question_3=self.cleaned_data['question_3'],
            answer_3=self.cleaned_data['answer_3'].lower().strip(),
            question_4=self.cleaned_data['question_4'],
            answer_4=self.cleaned_data['answer_4'].lower().strip(),
            question_5=self.cleaned_data['question_5'],
            answer_5=self.cleaned_data['answer_5'].lower().strip(),
        )
        security_questions.save()

        return user


class CustomLoginForm(LoginForm):
    """Custom login form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    """Custom password reset key form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })


class UserEmailForm(forms.ModelForm):
    """Form for updating user email."""

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'})


class ArtistForm(forms.ModelForm):
    """Form for adding/editing artists."""

    class Meta:
        model = Artist
        fields = ['Name']
        widgets = {
            'Name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter artist name'
            }),
        }


class AlbumForm(forms.ModelForm):
    """Form for adding/editing albums."""

    class Meta:
        model = Album
        fields = ['Title', 'ArtistId']
        widgets = {
            'Title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter album title'
            }),
            'ArtistId': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for adding/editing reviews."""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your review...'
            }),
        }
