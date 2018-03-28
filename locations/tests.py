"""Unit tests for Location."""
from django.utils import timezone
from rest_framework.test import APITestCase
from events.models import Event
from locations.models import Location
from bodies.models import Body
from roles.models import BodyRole
from roles.models import InstituteRole
from login.tests import get_new_user

class LocationTestCase(APITestCase):
    """Check if we can create locations."""

    test_body_1 = None
    reusable_test_location = None
    user = None
    insti_role = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.test_body_1 = Body.objects.create(name="TestBody1")
        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AddE,UpdE,DelE')
        self.user.profile.roles.add(self.body_1_role)

        self.insti_role = InstituteRole.objects.create(
            name="InstiRole", permissions='Location')

        self.reusable_test_location = Location.objects.create(
            name='TestLocation1', reusable=True)

    def test_event_link(self):
        """Test if events can be linked."""

        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venue_names": [self.reusable_test_location.name, 'DirectAddedVenue'],
            "bodies_id": [str(self.test_body_1.id)]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        test_event = Event.objects.get(id=response.data['id'])
        self.assertEqual(test_event.venues.get(
            id=self.reusable_test_location.id), self.reusable_test_location)

    def test_location_create(self):
        """Test if location can be created with institute role."""

        url = '/api/locations'
        data = {
            "name": "TestEvent1",
            "reusable": "true"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        self.user.profile.institute_roles.add(self.insti_role)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.user.profile.institute_roles.remove(self.insti_role)

    def test_location_update(self):
        """Test if location can be updated with body role or insti role."""

        location = Location.objects.create(name='TL', reusable=False)
        body = Body.objects.create(name="TestBody1")
        event = Event.objects.create(start_time=timezone.now(), end_time=timezone.now())
        body.events.add(event)
        event.venues.add(location)

        url = '/api/locations/' + str(location.id)
        data = {
            "name": "L2"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        role = BodyRole.objects.create(
            name="Body1Role", body=body, permissions='UpdE')
        self.user.profile.roles.add(role)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        data["reusable"] = "true"
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.user.profile.roles.remove(role)

        self.user.profile.institute_roles.add(self.insti_role)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.profile.institute_roles.remove(self.insti_role)

    def test_location_delete(self):
        """Check if location can be deleted with insti role."""

        location = Location.objects.create(name='TL', reusable=False)
        url = '/api/locations/' + str(location.id)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 403)

        self.user.profile.institute_roles.add(self.insti_role)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)
        self.user.profile.institute_roles.remove(self.insti_role)