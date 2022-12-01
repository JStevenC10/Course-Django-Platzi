from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question

import datetime
# Create your tests here.

# LO MAS COMUN ES TESTEAR MODELOS Y VISTAS
class QuestionModelTest(TestCase):
    
    def test_was_published_recently_with_future_question(self):
        'was_published_recently returns False for questions whose pub_date is in the future'
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text='¿Quien es el mejor cd de Platzi?', pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_past_question(self):
        'Pregunta publicada en el pasado'
        time = timezone.now() - datetime.timedelta(days=7)
        past_question = Question(question_text='¿Te gustan los nuevos cursos de python?', pub_date=time)
        self.assertIs(past_question.was_published_recently(), False)

    def test_was_published_recently_with_present_question(self):
        time = timezone.now()
        present_question = Question(question_text='¿Te gustan los nuevos cursos de python?', pub_date=time)
        self.assertIs(present_question.was_published_recently(), True)

def create_question(question_text, days):
    """FUNCTION FOR CREATE NEW QUESTION WITH GIVEN question_text AND days"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)
    

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        'if no question exist, an aproppiate message is displayed'
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls available!')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_no_future_question(self):
        'LAS PREGUNTAS DEL FUTURO NO DEBEN DESPLEGARSE EN EL INDEX'
        future_question = create_question('future question', 15)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls available!')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        'LAS PREGUNTAS PASADAS SI DEBEN DESPLEGARSE EN EL INDEX'
        past_question = create_question('past question', -10)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [past_question])

    def test_future_question_and_past_question(self):
        'EVEN IF BOOTH PAST AND FUTURE QUESTION EXIST, ONLY PAST QUESTION ARE DISPLAYED'
        past_question = create_question('past question', -30)
        future_question = create_question('future question', 15)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [past_question]
        )

    def test_two_past_question(self):
        'THE QUESTION INDEX PAGE MAY DISPLAY MULTIPLE QUESTIONS.'
        past_question1 = create_question(question_text='past question 1', days=-30)
        past_question2 = create_question(question_text='past question 2', days=-40)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [past_question1, past_question2]
        )
    
    def test_two_future_question(self):
        'THE QUESTION INDEX PAGE MAY DISPLAY MULTIPLE QUESTIONS.'
        future_question1 = create_question(question_text='future question 1', days=30)
        future_question2 = create_question(question_text='future question 2', days=25)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        'THE DETAIL VIEW OF A QUESTION WITH A pub_date IN THE FUTURE RETURN 404 ERROR'
        future_question = create_question(question_text='future question 1', days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        'THE DETAIL VIEW OF A QUESTION WITH A pub_date IN THE PAST DISPLAYED THE QUESTION DETAIL'
        past_question = create_question(question_text='past question 1', days=-30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
class QuestionResultViewTest(TestCase):

    def test_future_question_result(self):
        'NO PUEDEN VERSE LOS RESULTADOS DE UNA PREGUNTA QUE NO HA SIDO PUBLICADA'
        future_question = create_question(question_text='future question', days=30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

