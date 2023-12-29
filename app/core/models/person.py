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
    SET_NULL,
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
    featured_photo = ForeignKey(
        'PersonXPhoto', on_delete=SET_NULL,
        null=True, blank=True,
        related_name='+',
    )
    # DOB could be a property if I cared about storing month, day, and year
    # separately. Validation would become a combined check, depending on the
    # data. I think day requires a month, year cannot be future, year + month
    # cannot be future, year + month + day cannot be future, year + month +
    # day must validate into datetime.date

    music_albums = ManyToManyField(
        'MusicAlbum', through='MusicAlbumXPerson',
        related_name='+', blank=True,
    )
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXPerson',
        related_name='+', blank=True,
    )
    musical_instruments = ManyToManyField(
        'MusicalInstrument', through='MusicalInstrumentXPerson',
        related_name='+', blank=True,
    )
    song_performances = ManyToManyField(
        'SongPerformance', through='PersonXSongPerformance',
        related_name='+', blank=True
    )

    def __str__(self) -> str:
        return f'{self.preferred_name}'

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
        values = []
        if self.first_name:
            values.append(self.first_name)
        if self.middle_name:
            values.append(self.middle_name)
        if self.last_name:
            values.append(self.last_name)
        if self.suffix:
            values.append(self.suffix)
        return ' '.join(values)

    @property
    def full_name(self) -> str:
        if not any((self.first_name, self.middle_name, self.last_name)):
            return self.preferred_name
        values = []
        if self.prefix:
            values.append(self.prefix)
        if self.first_name:
            values.append(self.first_name)
        if self.nickname:
            values.append(f'"{self.nickname}"')
        if self.middle_name:
            values.append(self.middle_name)
        if self.last_name:
            values.append(self.last_name)
        if self.suffix:
            values.append(self.suffix)
        return ' '.join(values)


class PersonXPersonRelation(BaseAuditable):
    """Hereditary relationships; permanent."""
    class Relation(TextChoices):
        BROTHER = 'BROTHER'
        CHILD = 'CHILD'
        DAUGHTER = 'DAUGHTER'
        FATHER = 'FATHER'
        GRANDCHILD = 'GRANDCHILD'
        GRANDDAUGHTER = 'GRANDDAUGHTER'
        GRANDFATHER = 'GRANDFATHER'
        GRANDMOTHER = 'GRANDMOTHER'
        GRANDPARENT = 'GRANDPARENT'
        GRANDSON = 'GRANDSON'
        MOTHER = 'MOTHER'
        PARENT = 'PARENT'
        SIBLING = 'SIBLING'
        SISTER = 'SISTER'
        SON = 'SON'

        @classmethod
        def get_child_members(cls):
            return (
                cls.CHILD,
                cls.DAUGHTER,
                cls.SON
            )

        @classmethod
        def get_parent_members(cls):
            return (
                cls.FATHER,
                cls.MOTHER,
                cls.PARENT,
            )

        @classmethod
        def get_sibling_members(cls):
            return (
                cls.BROTHER,
                cls.SIBLING,
                cls.SISTER,
            )

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
        CLASSMATE = 'CLASSMATE'
        FRIEND = 'FRIEND'
        HUSBAND = 'HUSBAND'
        INSTRUCTOR = 'INSTRUCTOR'
        PARTNER = 'PARTNER'
        SCHOOLMATE = 'SCHOOLMATE'
        SPOUSE = 'SPOUSE'
        STUDENT = 'STUDENT'
        TEACHER = 'TEACHER'
        WIFE = 'WIFE'

        @classmethod
        def get_partner_members(cls):
            return (
                cls.HUSBAND,
                cls.PARTNER,
                cls.SPOUSE,
                cls.WIFE,
            )

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


class PersonXVideoGame(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    video_game = ForeignKey(
        'VideoGame', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    notes = TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'video_game'),
                name='unique_person_x_video_game',
            )
        ]


class PersonXVideoGameXVideoGameRole(BaseAuditable):
    person_x_video_game = ForeignKey(
        PersonXVideoGame, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    role = ForeignKey(
        'VideoGameRole', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    notes = TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person_x_video_game', 'role'),
                name='unique_person_x_video_game_x_video_game_role'
            )
        ]
