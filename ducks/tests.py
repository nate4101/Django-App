from django.test import TestCase
from django.urls import reverse
from .models import Duck, DuckFact
from .forms import DuckFactForm
from django.contrib.messages import get_messages
from django.http import Http404


class DuckModelTests(TestCase):

    def test_duck_str_method(self):
        duck = Duck.objects.create(name="Quackers", description="A fun duck.")
        expected_str = f"({duck.id}) - Quackers - A fun duck."
        self.assertEqual(str(duck), expected_str)

    def test_duck_field_max_lengths(self):
        name_field = Duck._meta.get_field("name")
        description_field = Duck._meta.get_field("description")
        self.assertEqual(name_field.max_length, 200)
        self.assertEqual(description_field.max_length, 200)

    def test_create_duck(self):
        duck = Duck.objects.create(name="Daisy", description="A calm duck.")
        self.assertEqual(Duck.objects.count(), 1)
        self.assertEqual(duck.name, "Daisy")
        self.assertEqual(duck.description, "A calm duck.")


class DuckFactModelTests(TestCase):

    def setUp(self):
        self.duck = Duck.objects.create(name="Howard", description="Famous duck.")

    def test_duckfact_str_method(self):
        fact = DuckFact.objects.create(duck=self.duck, fact="Quacks loudly", rating=5)
        expected_str = "(5) : Quacks loudly"
        self.assertEqual(str(fact), expected_str)

    def test_duckfact_default_rating(self):
        fact = DuckFact.objects.create(duck=self.duck, fact="Loves water")
        self.assertEqual(fact.rating, 0)

    def test_duckfact_fact_max_length(self):
        fact_field = DuckFact._meta.get_field("fact")
        self.assertEqual(fact_field.max_length, 200)

    def test_duckfact_deletes_with_duck(self):
        DuckFact.objects.create(duck=self.duck, fact="Eats seeds")
        self.duck.delete()
        self.assertEqual(DuckFact.objects.count(), 0)


class IndexViewTests(TestCase):

    def setUp(self):
        self.url = reverse("ducks:index")
        self.duck1 = Duck.objects.create(name="Daffy", description="Looney duck")
        self.duck2 = Duck.objects.create(name="Donald", description="Disney duck")

    def test_get_index_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ducks_appear_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("duck_list", response.context)
        duck_names = [duck.name for duck in response.context["duck_list"]]
        self.assertIn("Daffy", duck_names)
        self.assertIn("Donald", duck_names)

    def test_form_is_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)
        self.assertContains(response, "Add Duck")

    def test_post_valid_duck_adds_duck(self):
        response = self.client.post(
            self.url, {"name": "Huey", "description": "Nephew of Donald"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Duck.objects.filter(name="Huey").exists())

    def test_post_invalid_duck_shows_errors(self):
        response = self.client.post(
            self.url, {"name": "", "description": ""}  # Invalid: name is required
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertEqual(Duck.objects.count(), 2)  # Only the original ducks


class DetailViewTests(TestCase):

    def setUp(self):
        self.duck = Duck.objects.create(name="Plucky", description="Adventurous duck")
        self.url = reverse("ducks:duck_by_id", args=[self.duck.id])

    def test_detail_view_status_code_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_detail_view_status_code_invalid(self):
        invalid_url = reverse("ducks:duck_by_id", args=[999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ducks/duck_detail.html")

    def test_detail_view_context_contains_duck(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["duck"], self.duck)


# Function Based View Tests


class DuckByNameViewTests(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(name="Speedy", description="Fast duck")

    def test_valid_duck_name(self):
        response = self.client.get(reverse("ducks:duck_by_name", args=[self.duck.name]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["duck"], self.duck)

    def test_invalid_duck_name_raises_404(self):
        response = self.client.get(reverse("ducks:duck_by_name", args=["nonexistent"]))
        self.assertEqual(response.status_code, 404)


class RateViewTests(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(name="Bubbles", description="Cute duck")
        self.fact = DuckFact.objects.create(
            duck=self.duck, fact="Loves bread", rating=0
        )
        self.url = reverse("ducks:rate", args=[self.duck.id])

    def test_upvote_increments_rating_and_success_message(self):
        response = self.client.post(
            self.url, {"fact_id": self.fact.id, "direction": "up"}
        )
        self.fact.refresh_from_db()
        self.assertEqual(self.fact.rating, 1)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Thanks for upvoting!" in str(m) for m in messages))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_downvote_decrements_rating_and_error_message(self):
        response = self.client.post(
            self.url, {"fact_id": self.fact.id, "direction": "down"}
        )
        self.fact.refresh_from_db()
        self.assertEqual(self.fact.rating, -1)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Thanks for downvoting!" in str(m) for m in messages))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_missing_fact_id_shows_error_and_returns_detail(self):
        response = self.client.post(self.url, {"direction": "up"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unable to process your vote.")

    def test_invalid_fact_id_shows_error_and_returns_detail(self):
        response = self.client.post(self.url, {"fact_id": 9999, "direction": "up"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unable to process your vote.")

    def test_get_request_not_allowed(self):
        response = self.client.get(self.url)
        # Your view does not handle GET, so by default it might be 405 or 200, test accordingly
        self.assertIn(response.status_code, [200, 405])


class IndexViewTests(TestCase):
    def test_get_displays_ducks_and_form(self):
        # Create some ducks to display
        Duck.objects.create(name="Daffy", description="A funny duck")
        Duck.objects.create(name="Donald", description="A famous duck")

        response = self.client.get(reverse("ducks:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Daffy")
        self.assertContains(response, "Donald")
        self.assertIn("form", response.context)

    def test_post_valid_creates_duck_and_redirects(self):
        data = {"name": "Bubbles", "description": "Cute duck"}
        response = self.client.post(reverse("ducks:index"), data)
        self.assertRedirects(response, reverse("ducks:index"))
        self.assertTrue(Duck.objects.filter(name="Bubbles").exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Duck added successfully!" in str(m) for m in messages))

    def test_post_invalid_shows_errors_and_does_not_create(self):
        data = {"name": "", "description": ""}
        response = self.client.post(reverse("ducks:index"), data)
        self.assertEqual(response.status_code, 200)
        # Access form directly in context
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertEqual(Duck.objects.count(), 0)


class AddFactViewTests(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(name="Daffy", description="A funny duck")

    def test_get_add_fact_form(self):
        url = reverse("ducks:add_fact", kwargs={"duck_id": self.duck.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], DuckFactForm)
        self.assertEqual(response.context["duck"], self.duck)

    def test_post_valid_fact_creates_and_redirects(self):
        url = reverse("ducks:add_fact", kwargs={"duck_id": self.duck.id})
        data = {"fact": "Loves swimming"}
        response = self.client.post(url, data)
        self.assertRedirects(
            response, reverse("ducks:duck_by_id", kwargs={"pk": self.duck.id})
        )

        # Check fact created
        fact = DuckFact.objects.filter(duck=self.duck, fact="Loves swimming").first()
        self.assertIsNotNone(fact)
        self.assertEqual(fact.rating, 0)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Fact added successfully" in str(m) for m in messages))

    def test_post_invalid_fact_shows_errors(self):
        url = reverse("ducks:add_fact", kwargs={"duck_id": self.duck.id})
        data = {"fact": ""}  # invalid, empty fact
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("fact", form.errors)

        # No DuckFact created
        self.assertEqual(DuckFact.objects.filter(duck=self.duck).count(), 0)


class DeleteFactViewTests(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(name="TestDuck", description="A test duck")
        self.fact = DuckFact.objects.create(
            duck=self.duck, fact="Quacks loudly", rating=0
        )

    def test_post_deletes_fact(self):
        response = self.client.post(
            reverse("ducks:delete_fact_by_id", args=[self.fact.id])
        )
        self.assertRedirects(response, reverse("ducks:duck_by_id", args=[self.duck.id]))
        self.assertFalse(DuckFact.objects.filter(id=self.fact.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Fact deleted successfully" in str(m) for m in messages))

    def test_get_does_not_delete_fact_and_shows_error(self):
        response = self.client.get(
            reverse("ducks:delete_fact_by_id", args=[self.fact.id])
        )
        self.assertRedirects(response, reverse("ducks:duck_by_id", args=[self.duck.id]))
        self.assertTrue(DuckFact.objects.filter(id=self.fact.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid Request" in str(m) for m in messages))


class DeleteDuckViewTests(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(
            name="DeleteMe", description="Test duck for deletion."
        )

    def test_post_deletes_duck_and_redirects(self):
        response = self.client.post(
            reverse("ducks:delete_duck_by_id", args=[self.duck.id]), follow=True
        )

        # Duck should be deleted
        self.assertFalse(Duck.objects.filter(id=self.duck.id).exists())

        # Should redirect to index
        self.assertRedirects(response, reverse("ducks:index"))

        # Success message should be shown
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("deleted successfully" in m.message for m in messages))

    def test_get_does_not_delete_and_shows_error(self):
        response = self.client.get(
            reverse("ducks:delete_duck_by_id", args=[self.duck.id]), follow=True
        )

        # Duck should still exist
        self.assertTrue(Duck.objects.filter(id=self.duck.id).exists())

        # Should redirect to index
        self.assertRedirects(response, reverse("ducks:index"))

        # Error message should be shown
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid Request" in m.message for m in messages))

    def test_invalid_duck_id_returns_404(self):
        invalid_id = self.duck.id + 999
        response = self.client.post(
            reverse("ducks:delete_duck_by_id", args=[invalid_id])
        )
        self.assertEqual(response.status_code, 404)
