from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from os import path
from account.models import User
from tagging.registry import register
from utils.language import LANG_CHOICE
from django.utils.translation import ugettext_lazy as _


class AliasValidator(RegexValidator):
    regex = r'^[a-z0-9]{2,30}$'
    message = _(
        'Enter a valid alias. Use letters and digits only.'
    )


class Problem(models.Model):

    alias_validator = AliasValidator()

    alias = models.CharField(_('Alias'), max_length=64, blank=True, validators=[alias_validator])
    title = models.CharField(_('Title'), max_length=192, blank=True)
    description = models.TextField(_('Description'), blank=True)
    input = models.TextField(_('Input'), blank=True)
    output = models.TextField(_('Output'), blank=True)
    sample = models.TextField(_('Sample'), blank=True)
    hint = models.TextField(_('Hint'), blank=True)
    source = models.CharField(_('Source'), max_length=128, blank=True)

    visible = models.BooleanField(default=False, db_index=True)
    maintaining = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    time_limit = models.IntegerField(_('Time Limit'), default=2000)
    memory_limit = models.IntegerField(_('Memory Limit'), default=256)
    checker = models.CharField(_('Checker'), blank=True, max_length=64)
    interactor = models.CharField(_('Interactor'), blank=True, max_length=64)
    validator = models.CharField(_('Validator'), blank=True, max_length=64)
    pretests = models.TextField(_('Pretest'), blank=True)
    cases = models.TextField(_('Cases'), blank=True)
    points = models.TextField(_('Points'), blank=True)

    well_form_policy = models.BooleanField('Well form policy')

    managers = models.ManyToManyField(User, related_name='managing_problems')

    def __str__(self):
        return '%d. %s' % (self.pk, self.title)

    class Meta:
        ordering = ["-pk"]

    @property
    def sample_list(self):
        """
        sample name list
        """
        return list(filter(lambda x: x, self.sample.split(',')))

    @property
    def pretest_list(self):
        return list(filter(lambda x: x, self.pretests.split(',')))

    @property
    def case_list(self):
        return list(filter(lambda x: x, self.cases.split(',')))

    @property
    def point_list(self):
        return list(map(int, list(filter(lambda x: x, self.points.split(',')))))  # point list should be as long as case list

    @property
    def sample_display(self):
        return [get_input_and_output_for_case(case) for case in self.sample_list]


register(Problem)


class SpecialProgram(models.Model):

    CATEGORIES = ((x, x) for x in ('checker', 'generator', 'interactor', 'validator'))

    fingerprint = models.CharField(max_length=64, primary_key=True)
    category = models.CharField(max_length=12, choices=CATEGORIES)
    filename = models.CharField(max_length=64)
    lang = models.CharField('language', max_length=12, choices=LANG_CHOICE, default='cpp')
    code = models.TextField(blank=True)
    builtin = models.BooleanField(default=False)

    def __str__(self):
        return '%s (%s)' % (self.filename, self.category.capitalize())


def get_input_and_output_for_case(case_hash):
    """
    :type case_hash: str
    :return: (input_data, output_data)
    """
    with open(path.join(settings.TESTDATA_DIR, case_hash + '.in'), 'r') as inf:
        input_data = inf.read()
    with open(path.join(settings.TESTDATA_DIR, case_hash + '.out'), 'r') as ouf:
        output_data = ouf.read()
    return (input_data, output_data)


def get_input_path(case_hash):
    return path.join(settings.TESTDATA_DIR, case_hash + '.in')


def get_output_path(case_hash):
    return path.join(settings.TESTDATA_DIR, case_hash + '.out')


class Skill(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    parent_id = models.IntegerField(default=-1)
    problem_list = models.TextField(blank=True)
    priority = models.IntegerField(default=0)

    @property
    def parsed_problem_list(self):
        return list(map(int, filter(lambda x: x, self.problem_list.split(','))))
