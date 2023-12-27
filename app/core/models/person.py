import datetime

from django.db.models import (
    CASCADE,
    CharField,
    CheckConstraint,
    DateField,
    F,
    ForeignKey,
    ManyToManyField,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    TextChoices,
    TextField,
    UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_date_not_future


class Person(BaseAuditable):
    """A person. Generally self-explanatory as an entity.

    Maybe a personal acquaintance, and/or a notable individual with some level
    of fame.
    """
    preferred_name = CharField(max_length=255)
    first_name = CharField(max_length=255, blank=True)
    middle_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255, blank=True)
    nickname = CharField(max_length=255, blank=True)
    prefix = CharField(
        max_length=31, blank=True,
        help_text="Title or Salutation"
    )
    suffix = CharField(max_length=31, blank=True)
    date_of_birth = DateField(
        null=True, blank=True,
        validators=[validate_date_not_future]
    )
    date_of_death = DateField(
        null=True, blank=True,
        validators=[validate_date_not_future]
    )
    notes = TextField(blank=True)

    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXPerson',
        related_name='+', blank=True,
    )
    musical_instruments = ManyToManyField(
        'MusicalInstrument', through='MusicalInstrumentXPerson',
        related_name='+', blank=True,
    )

    def __str__(self) -> str:
        return f'{self.full_name}'

    @property
    def age(self) -> int | None:
        if self.date_of_birth is None:
            return None
        reference_date = self.date_of_death or datetime.date.today()
        years = reference_date.year - self.date_of_birth.year
        months = reference_date.month - self.date_of_birth.month
        if months < 0:
            return years - 1
        if months == 0:
            days = reference_date.day - self.date_of_birth.day
            if days < 0:
                return years - 1
        return years

    @property
    def is_living(self) -> bool:
        return not self.date_of_death

    @property
    def birth_name(self) -> str:
        text = f'{self.first_name}'
        if self.middle_name:
            text += f' {self.middle_name}'
        if self.last_name:
            text += f' {self.last_name}'
        if self.suffix:
            text += f' {self.suffix}'
        return text

    @property
    def full_name(self) -> str:
        if self.preferred_name:
            return self.preferred_name
        text = f'{self.first_name}'
        if self.nickname:
            text += f' "{self.nickname}"'
        if self.middle_name:
            text += f' {self.middle_name}'
        if self.last_name:
            text += f' {self.last_name}'
        if self.suffix:
            text += f' {self.suffix}'
        return text


class PersonXPersonRelation(BaseAuditable):
    """Hereditary relationships; permanent."""
    class Relation(TextChoices):
        BROTHER = 'BROTHER'
        CHILD = 'CHILD'
        DAUGHTER = 'DAUGHTER'
        FATHER = 'FATHER'
        FRIEND = 'FRIEND'
        GRANDCHILD = 'GRANDCHILD'
        GRANDDAUGHTER = 'GRANDDAUGHTER'
        GRANDFATHER = 'GRANDFATHER'
        GRANDMOTHER = 'GRANDMOTHER'
        GRANDPARENT = 'GRANDPARENT'
        GRANDSON = 'GRANDSON'
        MOTHER = 'MOTHER'
        SIBLING = 'SIBLING'
        SISTER = 'SISTER'
        SON = 'SON'
    person_a = ForeignKey(
        Person, on_delete=CASCADE,
        related_name='+'
    )
    person_b = ForeignKey(
        Person, on_delete=CASCADE,
        related_name='+'
    )
    relation = CharField(
        max_length=13, choices=Relation.choices,
        help_text=(
            f"Relation FROM Person A TO Person B."
            f" Person A is Person B's ..."
        )
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person_a', 'person_b'),
                name='unique_person_x_person_relation'
            ),
            CheckConstraint(
                check=~Q(person_a=F('person_b')),
                name='person_x_person_relation_not_self'
            )
        ]


class PersonXPersonRelationship(BaseAuditable):
    class Relationship(TextChoices):
        HUSBAND = 'HUSBAND'
        INSTRUCTOR = 'INSTRUCTOR'
        PARTNER = 'PARTNER'
        SPOUSE = 'SPOUSE'
        STUDENT = 'STUDENT'
        TEACHER = 'TEACHER'
        WIFE = 'WIFE'

    person_a = ForeignKey(
        Person, on_delete=CASCADE,
        related_name='+'
    )
    person_b = ForeignKey(
        Person, on_delete=CASCADE,
        related_name='+'
    )
    relationship = CharField(
        max_length=10, choices=Relationship.choices, blank=True,
        help_text=(
            f"The relationship FROM person A TO person B."
            f" Person A is Person B's ..."
        )
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person_a', 'person_b'),
                name='unique_person_x_person_relationship'
            ),
            CheckConstraint(
                check=~Q(person_a=F('person_b')),
                name='person_x_person_relationship_not_self'
            )
        ]


class PersonXPersonRelationshipActivity(BaseAuditable):
    person_x_person_relationship = ForeignKey(
        PersonXPersonRelationship, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    from_year = PositiveSmallIntegerField()
    until_year = PositiveSmallIntegerField(null=True, blank=True)


class PersonXPhoto(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    photo = ForeignKey(
        'Photo', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'photo'),
                name='unique_person_x_photo'
            )
        ]


class PersonXSong(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song = ForeignKey(
        'Song', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'song'),
                name='unique_person_x_song'
            )
        ]


class PersonXSongArrangement(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_arrangement = ForeignKey(
        'SongArrangement', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'song_arrangement'),
                name='unique_person_x_song_arrangement'
            )
        ]


class PersonXSongPerformance(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_performance = ForeignKey(
        'SongPerformance', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'song_performance'),
                name='unique_person_x_song_performance'
            )
        ]
