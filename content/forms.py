from django import forms
from content.models import Level, LevelQuestion, LevelQuestionOption
from django.core.exceptions import ValidationError


class LevelForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(LevelForm, self).clean()
        order = cleaned_data.get('order')
        module = cleaned_data.get('module')

        if order and module:

            if Level.objects.filter(module=module, order=order).exclude(id=self.instance.id).exists():
                msg = "There is already a level in %s module with level number %s." % (module.name, order)
                self.add_error('order', msg)

    class Meta:
        model = Level
        fields = ('order', 'module',)


class LevelQuestionForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(LevelQuestionForm, self).clean()
        order = cleaned_data.get('order')
        level = cleaned_data.get('level')

        if order and level:
            if LevelQuestion.objects.filter(level=level, order=order).exclude(id=self.instance.id).exists():
                msg = "There is already a question in %s level with order number %s." % (level, order)
                self.add_error('order', msg)

    class Meta:
        model = LevelQuestion
        fields = ('order', 'level',)


class OptionsInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(OptionsInlineFormset, self).clean()
        count = 0
        has_correct = False

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            count += 1

            if form.cleaned_data.get('correct') is True:
                has_correct = True

        error_list = []

        if count < 2:
            error_list.append(ValidationError('A minimum of 2 question options must be added.', code='error1'))

        if not has_correct:
            error_list.append(ValidationError('One options needs to be marked as correct.', code='error2'))

        if error_list:
            raise ValidationError(error_list)

    def save(self, commit=True):
        options = super(OptionsInlineFormset, self).save(commit=False)
        if options:
            question = options[0].question

            count = 1
            for option in options:
                if option.name is None:
                    saved = False
                    while not saved:
                        name = '%s option %d' % (question.name, count)
                        try:
                            LevelQuestionOption.objects.get(name=name)
                            count += 1
                        except LevelQuestionOption.DoesNotExist:
                            option.name = name
                            saved = True
                option.save()
