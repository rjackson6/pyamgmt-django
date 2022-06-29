from django.db.utils import IntegrityError
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from pyamgmt.models import MusicArtist, VehicleMake


class MusicArtistTests(TestCase):
    def setUp(self) -> None:
        MusicArtist.objects.create(name='Dead Letter Circus')

    def test_unique(self):
        with self.assertRaises(IntegrityError, msg='Duplicate entry on MusicArtist.name was allowed.'):
            MusicArtist.objects.create(name='Dead Letter Circus')


class VehicleMakeTests(TestCase):
    def setUp(self) -> None:
        VehicleMake.objects.create(name='Mitsubishi')
        VehicleMake.objects.create(name='Toyota')

    def test_toyota(self):
        toyota = VehicleMake.objects.get(name='Toyota')
        self.assertEqual(toyota.name, 'Toyota')

    def test_mitsubishi(self):
        mitsubishi = VehicleMake.objects.get(name='Mitsubishi')
        self.assertEqual(mitsubishi.name, 'Mitsubishi')

    def test_unique(self):
        with self.assertRaises(IntegrityError, msg='Duplicate entry on Vehicle.name was allowed.'):
            VehicleMake.objects.create(name='Toyota')


class VehicleViewTests(TestCase):
    def setUp(self) -> None:
        VehicleMake.objects.create(name='Mitsubishi')
        VehicleMake.objects.create(name='Toyota')

    def test_first(self):
        response = self.client.get(reverse('pyamgmt:vehiclemake:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mitsubishi')
