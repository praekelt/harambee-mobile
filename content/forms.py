from django import forms
from content.models import Level, LevelQuestion
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


class QuestionInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(QuestionInlineFormset, self).clean()

        order_list = []

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            order = form.cleaned_data.get('order')
            if order is None:
                continue

            if not order in order_list:
                order_list.append(form.cleaned_data.get('order'))
            else:
                raise ValidationError([ValidationError('Question order numbers cannot repeat.', code='error1')])

        for count in (1, len(order_list)):
            if not count in order_list:
                raise ValidationError([ValidationError('Please ensure question order numbers start at 1 and '
                                                       'increment by 1 for each question added.',
                                                       code='error1')])


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